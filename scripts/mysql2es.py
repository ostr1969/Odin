import mysql.connector
from elasticsearch import Elasticsearch, helpers

BATCH_SIZE = 2000

# MySQL connection (server-side cursor)
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="mysql",
    password="rgb098",
    database="libgen"
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM updated")

es = Elasticsearch("http://localhost:9200")

def generate_batches():
    while True:
        rows = cursor.fetchmany(BATCH_SIZE)
        if not rows:
            break

        actions = []
        for row in rows:
            actions.append({
                "_index": "libgen",
                "_id": str(row["ID"])+"_"+row["MD5"],
                "_source": row
            })

        yield from actions

helpers.bulk(es, generate_batches(), chunk_size=BATCH_SIZE)

cursor.close()
conn.close()