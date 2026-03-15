from flask import Flask, render_template, request, jsonify

import config,copy
from config import es
from utils import check_es_alive, get_topics_dn

from flask import session,redirect, url_for
app = Flask(__name__)
app.secret_key = 'some_secret0'

def build_query(filters):
    must = []

    for f in filters:
        field = f["field"]

        if field == "abstract+title":
            must.append({
                "query_string": {
                    "query": f["value"],
                    "fields": ["abstract", "title"]
                }
            })
        elif field == "publication_year":
            rng = {}
            if f.get("from"):
                rng["gte"] = int(f["from"])
            if f.get("to"):
                rng["lte"] = int(f["to"])

            if rng:
                must.append({"range": {"publication_year": rng}})
        elif field == "ngrams*":
            must.append({
                "query_string": {
                    "query": f["value"],
                    "fields": ["ngrams*"]
                }
            })  
        elif field == "id": 
              if "openalex" in f.get("value"):
                s=f.get("value")
              else:
                s="https://openalex.org/"+f.get("value")   
              must.append({"match": {field: s}})   
        else:
            if f.get("value"):
                must.append({"match": {field: f["value"]}})
    query={"query": {"bool": {"must": must}},"size":100}
    #print(query)
    return query

@app.route("/", methods=["GET", "POST"])
def home():
    redir=request.args.get("_redir")
    redirected = redir == "1"

    results = []
    selected_index = None
    q = ""
    filters = []
    total=0
    topics=[]
    topicsdict={}
    if request.method == "POST":
        session['index'] = request.form.get("index",None)  # Store selected index in session
        session['q'] = request.form.get("q", "")  # Store search query in session
        session['fields'] = request.form.getlist("field[]")  # Store fields in session
        session['values'] = request.form.getlist("value[]")  # Store values in session
        session['years_from'] = request.form.getlist("year_from[]")  # Store year_from in session
        session['years_to'] = request.form.getlist("year_to[]")  # Store year_to in session
        session['topic_filters'] = request.form.getlist("topic[]")  # Store topic filters in session        
        
        return redirect(url_for('home',_redir=1))  # Redirect to GET route to display results
    if not redirected: #means we got here from GET but not from redirection
        print("Not redirected, clearing session")
        session.clear()

    selected_index = session.get('index', "")
    q = session.get('q', "")
    fields = session.get('fields', [])
    values = session.get('values', [])
    years_from = session.get('years_from', [])
    years_to = session.get('years_to', [])
    topic_filters = session.get('topic_filters', [])  # Retrieve topic filters from session 
    
    print("session in get:", session)    
    v_idx = 0
    y_idx = 0
    
    for f in fields:
        if f == "publication_year":
            frm = years_from[y_idx] if y_idx < len(years_from) else None
            to = years_to[y_idx] if y_idx < len(years_to) else None
            filters.append({"field": f, "from": frm, "to": to})
            y_idx += 1
        else:
            val = values[v_idx] if v_idx < len(values) else None
            filters.append({"field": f, "value": val})
            v_idx += 1
    #print("topic_filters:",topic_filters)
    topics_must={"terms": {"topics.id": topic_filters}}
    
    body = build_query( filters)
    if len(topic_filters)>0:
        body["query"]["bool"]["must"].append(topics_must)
    if len(filters)>0 :
        res = es.search(
            index=selected_index,
            body={
                **body,
                "aggs": {
                    "topics": {
                        "terms": {
                            "field": "topics.id",
                            "size": 10
                            }
                    }
                }
            }
        )
        topics = res["aggregations"]["topics"]["buckets"]
        #print("topics:",topics)
        total = res["hits"]["total"]["value"]
        results = [hit["_source"] for hit in res["hits"]["hits"]]
        topicsdict=get_topics_dn(topics,index=selected_index)
       
    return render_template(
        "index.html",
        indexes=config.INDEXES,
        selected_index=selected_index,
        search_fields=config.SEARCH_FIELDS,
        small_fields=config.SMALL_FIELDS,
        displayed_fields=config.DISPLAYED_FIELDS,
        results=results,
        filters=filters,
        q=q,
        total=total,
        topics=topicsdict
    )


@app.route("/aggregations/<index>/<field>")
def aggs(index, field):
    body = {
        "size": 0,
        "aggs": {
            "values": {
                "terms": {"field": f"{field}", "size": 50}
            }
        }
    }
    
    res = es.search(index=index, body=body)
    buckets = res["aggregations"]["values"]["buckets"]
    print("Aggregation:", buckets)
    k="key"
    if field=="open_access.is_oa":
        k="key_as_string"
    return jsonify([b[k] for b in buckets])

if __name__ == "__main__":
    check_es_alive()
    app.run(debug=True,host="0.0.0.0",port=5002)
