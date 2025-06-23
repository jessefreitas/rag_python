#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print("🔍 DIAGNÓSTICO DE VETORIZAÇÃO")
    print("=" * 40)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="rag_system", 
            user="postgres",
            password="postgres"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verificar documentos sem chunks
            cur.execute("""
                SELECT d.id, d.file_name, d.agent_id
                FROM documents d
                LEFT JOIN document_chunks dc ON d.id = dc.document_id
                WHERE dc.id IS NULL
            """)
            docs_without_chunks = cur.fetchall()
            
            if docs_without_chunks:
                print(f"⚠️  PROBLEMA: {len(docs_without_chunks)} documentos sem chunks!")
                for doc in docs_without_chunks[:5]:
                    print(f"   - {doc['file_name']} (ID: {doc['id'][:8]}...)")
            else:
                print("✅ Todos os documentos possuem chunks")
            
            # Verificar totais
            cur.execute("SELECT COUNT(*) as count FROM documents")
            doc_count = cur.fetchone()["count"]
            
            cur.execute("SELECT COUNT(*) as count FROM document_chunks")
            chunk_count = cur.fetchone()["count"]
            
            print(f"📄 Documentos: {doc_count}")
            print(f"🧩 Chunks: {chunk_count}")
            
            # Verificar agente padrão
            cur.execute("SELECT id, name FROM agentes WHERE name LIKE '%Padrão%' OR name LIKE '%Sistema%'")
            default_agents = cur.fetchall()
            if default_agents:
                print(f"🤖 Agentes padrão: {len(default_agents)}")
            else:
                print("⚠️  Nenhum agente padrão encontrado")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 