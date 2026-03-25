from flask import Flask, jsonify, render_template, request, redirect, session, url_for
import config
from utils import firstsearch,build_query,get_topics_dn,get_concepts_dn

app = Flask(__name__)
app.secret_key = "your_secret_key"  # required for session

@app.route("/")
def home():
    return render_template(
        "home.html",
        indexes=config.INDEXES,
        fields=config.SEARCH_FIELDS,
        query="",
        index=config.INDEXES[0],
        field=config.SEARCH_FIELDS[0],
        show_button=False
    )

@app.route("/search", methods=["POST","GET"])
def search():
    redir=request.args.get("_redir")
    redirected = redir == "1"
    if "filters" not in session:        
       session["filters"] = {}

    
    if request.method == "POST":
        session['index'] = request.form.get("index",None)  # Store selected index in session
        session['query'] = request.form.get("query", "")  # Store search query in session
        session['field'] = request.form.get("field")  # Store field in session
        #session['values'] = request.form.getlist("value[]")  # Store values in session
        #session['years_from'] = request.form.getlist("year_from[]")  # Store year_from in session
        #session['years_to'] = request.form.getlist("year_to[]")  # Store year_to in session
        #session['topic_filters'] = request.form.getlist("topic[]")  # Store topic filters in session        
        
        return redirect(url_for('search',_redir=1))  # Redirect to GET route to display results
    # if not redirected: #means we got here from GET but not from redirection
    #     print("Not redirected, clearing session")
    #     session.clear()
    ind=request.form.get("index")
    filters=[{"field":session["field"],"value":session["query"]}]
    if session["filters"].get("dchoice") == "0":
        filters.append({"field":"publication_year","from":2025,"to":3000})
    elif session["filters"].get("dchoice") == "1":
        filters.append({"field":"publication_year","from":2020,"to":3000})
    elif session["filters"].get("dchoice") == "custom":       
        filters.append({"field":"publication_year","from":session["filters"].get("from_year"),
                        "to":session["filters"].get("to_year")})
    if session["filters"].get("type_filters"):
        filters.append({"field":"type","value":session["filters"].get("type_filters")}) 
    if session["filters"].get("topic_filters"):
        filters.append({"field":"topics.id","value":session["filters"].get("topic_filters")}) 
    if session["filters"].get("concept_filters"):
        filters.append({"field":"concepts.id","value":session["filters"].get("concept_filters")})             
    if session["filters"].get("language_filters"):
        filters.append({"field":"language","value":session["filters"].get("language_filters")}) 
    if session.get("oa_filter"):
        filters.append({"field":"primary_location.is_oa","value":True})  
    res=firstsearch(filters,ind)  
    if res is not None:
        topics = res["aggregations"]["topics"]["buckets"]
        topicsdn=get_topics_dn(topics,index=ind)
        concepts = res["aggregations"]["concepts"]["buckets"]
        conceptsdn=get_concepts_dn(concepts,index=ind)
        types = res["aggregations"]["types"]["buckets"]
        languages = res["aggregations"]["language"]["buckets"]
        total = res["hits"]["total"]["value"] 
    return render_template(
        "search.html",
        indexes=config.INDEXES,
        fields=config.SEARCH_FIELDS,
        query=session.get("query"),
        index=session.get("index"),
        field=session.get("field"),
        show_button=True,
        displayed_fields=config.DISPLAYED_FIELDS,
        results=res["hits"]["hits"],
        types=types,
        topics=topicsdn,
        concepts=conceptsdn,
        languages=languages,
        total=total
    )

@app.route("/set_year_filter",methods=["POST"])
def setyearfilter():
    #year=request.form.get("year")
    opt=request.form.get("opt")
    
    if opt=="2025":
        session["filters"]["dchoice"]="0"
    elif opt=="2020":    
        session["filters"]["dchoice"]="1"
    elif opt=="2":
        session["filters"]["dchoice"]="custom"
        session["filters"]["from"]=request.form.get("year_from")
        session["filters"]["to"]=request.form.get("year_to")
    else :
        session["filters"].pop("dchoice", None) 
    session.modified = True       
    return jsonify({"success": True})
@app.route("/set_doc_types", methods=["POST"])
def set_doc_types():
    selected = request.form.getlist("doc_types")  # multiple values
    session["filters"]["type_filters"] = selected
    session.modified = True
    return jsonify({"success": True})
@app.route("/results")
def results():
    return f"""
    Query: {session.get('query')}<br>
    Index: {session.get('index')}<br>
    Field: {session.get('field')}
    """

if __name__ == "__main__":
    app.run(debug=True)