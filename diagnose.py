import psycopg2
from psycopg2.extras import RealDictCursor

print("Diagnostico de vetorizacao")
conn = psycopg2.connect(host="localhost", database="rag_system", user="postgres", password="postgres")
cur = conn.cursor(cursor_factory=RealDictCursor)

cur.execute("SELECT COUNT(*) as count FROM documents")
docs = cur.fetchone()["count"]

cur.execute("SELECT COUNT(*) as count FROM document_chunks") 
chunks = cur.fetchone()["count"]

cur.execute("SELECT d.id, d.file_name FROM documents d LEFT JOIN document_chunks dc ON d.id = dc.document_id WHERE dc.id IS NULL")
missing = cur.fetchall()

print(f"Documentos: {docs}")
print(f"Chunks: {chunks}")
print(f"Documentos sem chunks: {len(missing)}")

conn.close()
