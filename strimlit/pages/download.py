import streamlit as st
from config import es,open_file_types 
from shutil import copyfile
id_value = st.query_params.get("id")
ind=st.query_params.get("index","works3")
hit = es.get(index=ind, id=id_value)
path = hit["_source"]["path"]["real"]
# change base path in case files were moved after indexing
# for base_path, new_path in CONFIG["base_paths"].items():
#     if path.lower().startswith(base_path.lower()):
#         path = path.replace(base_path, new_path)
ext = hit["_source"]["file"]["extension"]
target = "files/{}.{}".format(id_value, ext)
copyfile(path, target)
if ext.lower() in open_file_types:
    download = False
else:
    download = True
return send_file(target, as_attachment=download)
