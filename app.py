from flask import Flask, render_template, request, jsonify

import config,copy
from config import es
from utils import get_topics_dn
app = Flask(__name__)


def build_query(q, filters):
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
        else:
            if f.get("value"):
                must.append({"match": {field: f["value"]}})
    query={"query": {"bool": {"must": must}},"size":100}
    #print(query)
    return query

@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    selected_index = None
    q = ""
    filters = []
    total=0
    topics=[]
    if request.method == "POST":
        selected_index = request.form["index"]
        q = request.form.get("q", "")

        fields = request.form.getlist("field[]")
        values = request.form.getlist("value[]")
        years_from = request.form.getlist("year_from[]")
        years_to = request.form.getlist("year_to[]")   
        topic_filters = request.form.getlist("topic[]")  # selected topics 
        
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
        
        body = build_query(q, filters)
        if len(topic_filters)>0:
            body["query"]["bool"]["must"].append(topics_must)
        
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
        #print(topics)
        total = res["hits"]["total"]["value"]
        results = [hit["_source"] for hit in res["hits"]["hits"]]
        topics=get_topics_dn(topics,index=selected_index)
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
        topics=topics
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
    return jsonify([b["key"] for b in buckets])

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5002)
