import os
from pathlib import Path
import shutil

from flask import Flask, jsonify, render_template, request, redirect, send_file, session, url_for
import config
from utils import firstsearch,build_query,get_topics_dn,get_concepts_dn,aggsearch,get_filters

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
    #redir=request.args.get("_redir")
    #redirected = redir == "1"
    if "filters" not in session:        
       session["filters"] = {}
    if "active" not in  session["filters"]:  
       session["filters"]["active"]=[]
       
      

    
    if request.method == "POST":
        session['index'] = request.form.get("index",None)  # Store selected index in session
        session['query'] = request.form.get("query", "")  # Store search query in session
        session['field'] = request.form.get("field")  # Store field in session
       
        return redirect(url_for('search'))  # Redirect to GET route to display results
    
    ind=request.form.get("index")
    filters=get_filters(session)
    
    res=firstsearch(filters,ind)  
    if res is not None:
        
        total = res["hits"]["total"]["value"] 
        results=[]
        for rec in res['hits']['hits']:
            r=rec['_source']
            if r.get("type")=="book" or r.get("type")=="book-chapter":
                icon="📚"
            elif r.get("type")=="article":
                icon="📄"
            elif r.get("type")=="chapter":
                icon="📖"
            elif r.get("type")=="dataset":
                icon="📦"
            elif r.get("type")=="dissertation":
                icon="🎓"
            else:                icon="📁"
            r['icon']=icon
            results.append(rec)
    return render_template(
        "search.html",
        indexes=config.INDEXES,
        fields=config.SEARCH_FIELDS,
        query=session.get("query"),
        index=session.get("index"),
        field=session.get("field"),
        show_button=True,
        displayed_fields=config.DISPLAYED_FIELDS,
        results=results,
       
        total=total,
        active=session["filters"]["active"]
    )

@app.route("/set_year_filter",methods=["POST"])
def setyearfilter():
    #year=request.form.get("year")
    opt=request.form.get("opt")
    
    if opt=="2025":
        session["filters"]["dchoice"]="0"
        
        session["filters"]["active"].append("year")
    elif opt=="2020":    
        session["filters"]["dchoice"]="1"
        session["filters"]["active"].append("year")
    elif opt=="2":
        session["filters"]["dchoice"]="custom"
        session["filters"]["from"]=request.form.get("year_from")
        session["filters"]["to"]=request.form.get("year_to")
        session["filters"]["active"].append("year")
    else :
        session["filters"].pop("dchoice", None) 
        session["filters"]["active"].remove("year")
    session.modified = True       
    return jsonify({"success": True})
@app.route("/set_types_filter", methods=["POST"])
def set_doc_types():
    selected = request.form.getlist("checkboxes")  # multiple values
    session["filters"]["type_filters"] = selected
    if len(selected)>0:
        session["filters"]["active"].append("type")
    else:
        session["filters"]["active"].remove("type")
    session.modified = True
    return jsonify({"success": True})
@app.route("/set_lang_filter", methods=["POST"])
def set_langs():
    selected = request.form.getlist("checkboxes")  # multiple values
    session["filters"]["language_filters"] = selected
    if len(selected)>0:
        session["filters"]["active"].append("lang")
    else:
        session["filters"]["active"].remove("lang")
    session.modified = True
    return jsonify({"success": True})
@app.route("/set_topics_filter", methods=["POST"])
def set_topics():
    selected = request.form.getlist("checkboxes")  # multiple values
    session["filters"]["topic_filters"] = selected
    if len(selected)>0:
        session["filters"]["active"].append("topics")
    else:
        session["filters"]["active"].remove("topics")
    session.modified = True
    return jsonify({"success": True})
@app.route("/set_concepts_filter", methods=["POST"])
def set_concepts():
    selected = request.form.getlist("checkboxes")  # multiple values
    session["filters"]["concept_filters"] = selected
    if len(selected)>0:
        session["filters"]["active"].append("concepts")
    else:
        session["filters"]["active"].remove("concepts")
    session.modified = True
    return jsonify({"success": True})
@app.route("/set_oa_filter", methods=["POST"])
def setoafilter():
    data = request.get_json()
    if data.get("oa_filter") == "1":
        session["filters"]["oa_filter"]=True
        session["filters"]["active"].append("oa")
    else:
        session["filters"].pop("oa_filter",None)
        session["filters"]["active"].remove("oa")
    session.modified = True
    return jsonify({"success": True})
@app.route("/clear_filters", methods=["POST"])
def clear_filters():
    session.pop("filters", None)   # remove key safely
    session.modified = True
    return jsonify({"success": True})
@app.route("/get_agg/<aggby>")
def get_agg(aggby):
    #print("aggby:",aggby)
    ind=session.get("index")
    filters=get_filters(session)
    res=aggsearch(filters,ind,aggby)
    if aggby in ["type","language"]:
        aggs = res["aggregations"]["somename"]["buckets"]
    elif aggby=="topics.id" :   
        topics = res["aggregations"]["somename"]["buckets"]
        aggs=get_topics_dn(topics,index=ind)
    elif aggby=="concepts.id":    
        concepts = res["aggregations"]["somename"]["buckets"]
        aggs=get_concepts_dn(concepts,index=ind)
        
    #print(aggs)   
    return jsonify({"types": aggs})
@app.route("/session")
def results():
    return jsonify(dict(session))
@app.route("/json/<id>")
def showjson(id):
    index=session.get("index")
    res=config.es.get(index=index,id=id)
    return jsonify(res['_source'])
@app.route("/download/<id>")
def download(id):
    index=session.get("index")
    path=config.es.get(index=index,id=id)["_source"].get("path","")
    
   
    path=r"/workspace/Aftabi.pdf"
    
    #open file server on the root of the files by "python -m http.server 8000"
    local_url = f"http://localhost:8000/{path}"

    filename = Path(path).name
    ext = Path(path).suffix
    
        # --- Non-PDF: copy + load ---
    local_path = os.path.join(config.FILES_DIR, id+ext)
        #print(FILES_DIR,id1+ext)

        # Copy only once
    if not os.path.exists(local_path):            
            shutil.copyfile(path, local_path)
    
    if ext.lower().replace(".","")  in config.OPEN_FILE_TYPES:
        download = False
    else:
        download = True
    return send_file(local_path, as_attachment=download)


if __name__ == "__main__":
    app.run(debug=True)