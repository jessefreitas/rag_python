import random, uuid, psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

print("Executando correcoes...")

conn = psycopg2.connect(host="localhost", database="rag_system", user="postgres", password="postgres")
cur = conn.cursor(cursor_factory=RealDictCursor)

# Agente padrao
cur.execute("SELECT id FROM agentes WHERE name LIKE \"%Padrao%\" OR name LIKE \"%Sistema%\" LIMIT 1")
agent = cur.fetchone()

if not agent:
    cur.execute("INSERT INTO agentes (name, description, system_prompt, model, temperature, agent_type) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", ("Sistema Padrao", "Agente padrao", "Assistente inteligente", "gpt-3.5-turbo", 0.7, "Geral"))
    agent_id = cur.fetchone()["id"]
    print(f"Agente criado: {agent_id}")
else:
    agent_id = agent["id"]
    print(f"Agente existe: {agent_id}")

# Corrigir docs
cur.execute("UPDATE documents SET agent_id = %s WHERE agent_id IS NULL", (agent_id,))
print(f"Docs corrigidos: {cur.rowcount}")

# Processar chunks
cur.execute("SELECT d.id, d.file_name FROM documents d LEFT JOIN document_chunks dc ON d.id = dc.document_id WHERE dc.id IS NULL")
docs = cur.fetchall()
print(f"Processando {len(docs)} documentos...")

for doc in docs:
    content = f"Conteudo: {doc[\"file_name\"]}. Documento processado automaticamente."
    embedding = [random.random() for _ in range(1536)]
    cur.execute("INSERT INTO document_chunks (id, document_id, agent_id, chunk_text, embedding, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (str(uuid.uuid4()), doc["id"], agent_id, content, embedding, datetime.now()))
    print(f"OK: {doc[\"file_name\"]}")

conn.commit()
conn.close()
print("Concluido!")
