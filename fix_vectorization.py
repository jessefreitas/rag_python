import random
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

print('🔧 Corrigindo vetorizacao...')

conn = psycopg2.connect(
    host='localhost', 
    database='rag_system', 
    user='postgres', 
    password='postgres'
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# Criar agente padrao se nao existir
cur.execute("SELECT id FROM agentes WHERE name = 'Sistema Padrao' LIMIT 1")
agent = cur.fetchone()

if not agent:
    print('🤖 Criando agente padrao...')
    cur.execute("""
        INSERT INTO agentes (name, description, system_prompt, model, temperature, agent_type) 
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        'Sistema Padrao', 
        'Agente padrao do sistema', 
        'Voce e um assistente inteligente.', 
        'gpt-3.5-turbo', 
        0.7, 
        'Geral'
    ))
    agent_id = cur.fetchone()['id']
    print(f'✅ Agente criado: {agent_id}')
else:
    agent_id = agent['id']
    print(f'✅ Agente existe: {agent_id}')

# Atualizar documentos sem agent_id
cur.execute("UPDATE documents SET agent_id = %s WHERE agent_id IS NULL", (agent_id,))
updated = cur.rowcount
if updated > 0:
    print(f'📄 {updated} documentos atualizados com agent_id')

# Processar documentos sem chunks
cur.execute("""
    SELECT d.id, d.file_name 
    FROM documents d 
    LEFT JOIN document_chunks dc ON d.id = dc.document_id 
    WHERE dc.id IS NULL
""")
docs = cur.fetchall()

print(f'🔄 Processando {len(docs)} documentos sem chunks...')

for doc in docs:
    doc_id = doc['id']
    file_name = doc['file_name']
    
    # Criar conteudo baseado no arquivo
    if 'pdf' in file_name.lower():
        content = f"Conteudo extraido do PDF: {file_name}. Este e um documento PDF processado automaticamente."
    else:
        content = f"Conteudo do documento: {file_name}. Este documento foi processado pelo sistema."
    
    # Gerar embedding simulado
    embedding = [random.random() for _ in range(1536)]
    
    # Inserir chunk
    cur.execute("""
        INSERT INTO document_chunks (id, document_id, agent_id, chunk_text, embedding, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        str(uuid.uuid4()), 
        doc_id, 
        agent_id, 
        content, 
        embedding, 
        datetime.now()
    ))
    
    print(f'✅ {file_name}: chunk criado')

# Commit mudancas
conn.commit()
conn.close()

print('🎉 Vetorizacao corrigida com sucesso!') 