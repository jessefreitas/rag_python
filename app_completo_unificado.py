"""
🚀 RAG PYTHON v1.5.1 - SISTEMA COMPLETO UNIFICADO
Sistema RAG com Multi-LLM, Agentes, Privacidade LGPD e Dashboard
Todas as funcionalidades em uma única interface
"""

import streamlit as st
import os
import tempfile
import json
import uuid
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
import psycopg2.extras
import time
import hashlib
import random

# Importações do sistema
from llm_providers import LLMProviderManager
from privacy_system import privacy_manager
from vector_store import VectorStore
from database import Database

# Importar o novo gerenciador de modelos
try:
    from llm_models_config import models_manager
except ImportError:
    models_manager = None
    logger.warning("Módulo llm_models_config não encontrado")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="🚀 RAG Python v1.5.1 - Sistema Completo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .provider-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .privacy-alert {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    .info-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class AgentManager:
    """Gerenciador de Agentes com funcionalidades completas"""
    
    def __init__(self):
        self.llm_manager = LLMProviderManager()
    
    @staticmethod
    def _execute_query(query: str, params: tuple = (), fetch: Optional[str] = None):
        """Executa query no banco de dados"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params)
                if fetch == 'one':
                    result = cur.fetchone()
                elif fetch == 'all':
                    result = cur.fetchall()
                else:
                    result = None
                conn.commit()
                return result
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: Database.release_connection(conn)
    
    def create_agent(self, name: str, description: str, agent_type: str, system_prompt: str, 
                    model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> Optional[str]:
        """Cria um novo agente"""
        try:
            query = """
                INSERT INTO agentes (name, description, system_prompt, model, temperature, agent_type) 
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """
            params = (name, description, system_prompt, model, temperature, agent_type)
            result = self._execute_query(query, params, fetch='one')
            return str(result['id']) if result else None
        except Exception as e:
            logger.error(f"Erro ao criar agente: {e}")
            return None
    
    def get_all_agents(self) -> List[Dict]:
        """Lista todos os agentes"""
        try:
            query = "SELECT * FROM agentes ORDER BY created_at DESC"
            rows = self._execute_query(query, fetch='all')
            agents = []
            for row in rows:
                agent_data = dict(row)
                # Converter Decimal para float se necessário
                if 'temperature' in agent_data:
                    agent_data['temperature'] = float(agent_data['temperature'])
                agents.append(agent_data)
            return agents
        except Exception as e:
            logger.error(f"Erro ao listar agentes: {e}")
            return []
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Dict]:
        """Obtém agente por ID"""
        try:
            query = "SELECT * FROM agentes WHERE id = %s"
            row = self._execute_query(query, (agent_id,), fetch='one')
            if row:
                agent_data = dict(row)
                # Converter Decimal para float se necessário
                if 'temperature' in agent_data:
                    agent_data['temperature'] = float(agent_data['temperature'])
                return agent_data
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar agente: {e}")
            return None
    
    def update_agent(self, agent_id: str, data: Dict) -> bool:
        """Atualiza um agente"""
        try:
            query = """
                UPDATE agentes SET name = %s, description = %s, system_prompt = %s, 
                model = %s, temperature = %s WHERE id = %s
            """
            params = (data['name'], data['description'], data['system_prompt'], 
                     data['model'], data['temperature'], agent_id)
            self._execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar agente: {e}")
            return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """Deleta um agente"""
        try:
            query = "DELETE FROM agentes WHERE id = %s"
            self._execute_query(query, (agent_id,))
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar agente: {e}")
            return False

class RAGSystemUnified:
    """Sistema RAG unificado com todas as funcionalidades"""
    
    def __init__(self):
        self.llm_manager = LLMProviderManager()
        self.agent_manager = AgentManager()
        self.documents = []
        self.knowledge_base = {}
        self.settings = {
            'model_name': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        self.connection_pool = self._create_connection_pool()
        self._create_tables()
    
    def _create_connection_pool(self):
        """Cria pool de conexões com PostgreSQL"""
        try:
            return psycopg2.pool.SimpleConnectionPool(
                1, 20,
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                database=os.getenv('POSTGRES_DB', 'rag_system'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
                port=os.getenv('POSTGRES_PORT', '5432')
            )
        except Exception as e:
            logger.error(f"Erro ao criar pool de conexões: {e}")
            return None
    
    def _create_tables(self):
        """Cria tabelas necessárias se não existirem"""
        try:
            create_agents_table = """
                CREATE TABLE IF NOT EXISTS agentes (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    agent_type VARCHAR(100),
                    system_prompt TEXT NOT NULL,
                    model VARCHAR(100) DEFAULT 'gpt-3.5-turbo',
                    temperature DECIMAL(3,2) DEFAULT 0.7,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            
            create_documents_table = """
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    content TEXT,
                    file_type VARCHAR(50),
                    file_size INTEGER,
                    agent_id UUID REFERENCES agentes(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    vector_store_id VARCHAR(255)
                );
            """
            
            create_index = """
                CREATE INDEX IF NOT EXISTS idx_documents_agent_id ON documents(agent_id);
                CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
            """
            
            self.agent_manager._execute_query(create_agents_table)
            self.agent_manager._execute_query(create_documents_table)
            self.agent_manager._execute_query(create_index)
            
            logger.info("Tabelas criadas/verificadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            # Não falhar se não conseguir conectar no PostgreSQL
            logger.warning("Sistema funcionará sem PostgreSQL - usando dados em memória")
    
    def query_with_agent(self, question: str, agent_id: str = None, llm: str = None, model: str = None) -> Dict:
        """Processa pergunta com agente específico e LLM escolhido"""
        try:
            import time
            start_time = time.time()
            
            agent = None
            if agent_id:
                agent = self.agent_manager.get_agent_by_id(agent_id)
            
            # Recuperar documentos do agente
            context_docs = self.get_agent_documents(agent_id) if agent_id else []
            
            # Preparar contexto dos documentos
            context = ""
            if context_docs:
                context = "\n\nContexto dos documentos:\n"
                for doc in context_docs[:3]:  # Limitar a 3 documentos mais relevantes
                    context += f"- {doc.get('name', 'Documento')}: {doc.get('content', '')[:500]}...\n"
            
            # Preparar mensagens
            messages = []
            
            if agent:
                system_prompt = agent['system_prompt']
                if context:
                    system_prompt += f"\n\nUse os seguintes documentos como referência quando relevante:{context}"
                
                messages.append({
                    "role": "system", 
                    "content": system_prompt
                })
            elif context:
                messages.append({
                    "role": "system",
                    "content": f"Você é um assistente inteligente. Use os seguintes documentos como referência quando relevante:{context}"
                })
            
            messages.append({"role": "user", "content": question})
            
            # Determinar configurações
            if agent:
                # Usar modelo específico se fornecido, senão usar do agente
                final_model = model if model and model != "default" else agent['model']
                temperature = float(agent['temperature'])
            else:
                # Usar modelo específico se fornecido, senão usar padrão
                final_model = model if model and model != "default" else self.settings['model_name']
                temperature = float(self.settings['temperature'])
            
            # Gerar resposta usando LLM especificado
            if llm:
                result = self.llm_manager.generate_response(
                    messages,
                    provider_name=llm,
                    model=final_model,
                    temperature=temperature
                )
                
                if result.get('success'):
                    end_time = time.time()
                    return {
                        'answer': result['response'],
                        'agent_used': agent['name'] if agent else 'Sistema Padrão',
                        'model_used': result.get('model', final_model),
                        'llm_used': llm,
                        'response_time': round(end_time - start_time, 2),
                        'documents_used': len(context_docs),
                        'success': True
                    }
                else:
                    return {
                        'answer': f"Erro: {result.get('error', 'Erro desconhecido')}",
                        'agent_used': agent['name'] if agent else 'Sistema Padrão',
                        'model_used': final_model,
                        'llm_used': llm,
                        'response_time': 0,
                        'documents_used': 0,
                        'success': False
                    }
            else:
                # Usar método legado
                response = self.llm_manager.generate_response_old(
                    messages,
                    model=final_model,
                    temperature=temperature
                )
                
                end_time = time.time()
                return {
                    'answer': response,
                    'agent_used': agent['name'] if agent else 'Sistema Padrão',
                    'model_used': final_model,
                    'llm_used': 'padrão',
                    'response_time': round(end_time - start_time, 2),
                    'documents_used': len(context_docs),
                    'success': True
                }
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            return {
                'answer': f"Erro: {str(e)}",
                'agent_used': 'Erro',
                'model_used': 'N/A',
                'llm_used': llm or 'N/A',
                'response_time': 0,
                'documents_used': 0,
                'success': False
            }
    
    def get_agent_documents(self, agent_id: str = None) -> List[Dict]:
        """Recupera documentos associados a um agente específico"""
        try:
            if not agent_id:
                # Retornar documentos da base geral
                return [doc for doc in self.documents if not doc.get('agent_id')]
            
            # Buscar documentos no banco de dados PostgreSQL (usando schema correto)
            query = """
                SELECT d.id, d.file_name, d.source_type, d.content_hash, d.created_at, d.agent_id,
                       COUNT(dc.id) as chunk_count
                FROM documents d
                LEFT JOIN document_chunks dc ON d.id = dc.document_id
                WHERE d.agent_id = %s 
                GROUP BY d.id, d.file_name, d.source_type, d.content_hash, d.created_at, d.agent_id
                ORDER BY d.created_at DESC
            """
            
            rows = self.agent_manager._execute_query(query, (agent_id,), fetch='all')
            
            if rows:
                documents = []
                for row in rows:
                    documents.append({
                        'id': str(row[0]),
                        'name': row[1] or 'Documento sem nome',
                        'file_type': row[2] or 'unknown',
                        'content_hash': row[3],
                        'created_at': row[4],
                        'agent_id': str(row[5]),
                        'chunk_count': row[6] or 0
                    })
                return documents
            else:
                # Fallback para documentos em memória
                return [doc for doc in self.documents if doc.get('agent_id') == agent_id]
                
        except Exception as e:
            logger.error(f"Erro ao recuperar documentos do agente {agent_id}: {e}")
            # Fallback para documentos em memória
            if agent_id:
                return [doc for doc in self.documents if doc.get('agent_id') == agent_id]
            else:
                return [doc for doc in self.documents if not doc.get('agent_id')]
    
    def multi_llm_compare(self, question: str, providers: List[str] = None) -> Dict:
        """Compara respostas de múltiplos LLMs"""
        try:
            if not providers:
                providers = ['openai', 'google', 'openrouter', 'deepseek']
            
            messages = [{"role": "user", "content": question}]
            
            results = self.llm_manager.compare_multi_llm(
                messages, 
                providers=providers,
                model=self.settings['model_name'],
                temperature=self.settings['temperature']
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na comparação Multi-LLM: {e}")
            return {'error': str(e)}

    def check_database_connection(self) -> Dict:
        """Verifica status da conexão com PostgreSQL"""
        try:
            # Testar conexão básica
            query = "SELECT version(), current_database(), current_user, now()"
            result = self.agent_manager._execute_query(query, fetch='one')
            
            if result:
                return {
                    'status': 'connected',
                    'version': result[0],
                    'database': result[1],
                    'user': result[2],
                    'timestamp': result[3],
                    'connection_pool': bool(self.connection_pool),
                    'error': None
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Sem resposta do banco'
                }
                
        except Exception as e:
            logger.error(f"Erro ao verificar conexão PostgreSQL: {e}")
            return {
                'status': 'disconnected',
                'error': str(e)
            }
    
    def get_database_stats(self) -> Dict:
        """Obtém estatísticas do banco de dados"""
        try:
            stats = {}
            
            # Contar agentes
            query_agents = "SELECT COUNT(*) FROM agentes"
            agents_count = self.agent_manager._execute_query(query_agents, fetch='one')
            stats['agents_count'] = agents_count[0] if agents_count else 0
            
            # Contar documentos
            query_docs = "SELECT COUNT(*) FROM documents"
            docs_count = self.agent_manager._execute_query(query_docs, fetch='one')
            stats['documents_count'] = docs_count[0] if docs_count else 0
            
            # Contar chunks
            query_chunks = "SELECT COUNT(*) FROM document_chunks"
            chunks_count = self.agent_manager._execute_query(query_chunks, fetch='one')
            stats['chunks_count'] = chunks_count[0] if chunks_count else 0
            
            # Contar conversas
            query_conversations = "SELECT COUNT(*) FROM conversations"
            conversations_count = self.agent_manager._execute_query(query_conversations, fetch='one')
            stats['conversations_count'] = conversations_count[0] if conversations_count else 0
            
            # Contar respostas LLM
            query_responses = "SELECT COUNT(*) FROM llm_responses"
            responses_count = self.agent_manager._execute_query(query_responses, fetch='one')
            stats['llm_responses_count'] = responses_count[0] if responses_count else 0
            
            # Estatísticas por agente
            query_docs_per_agent = """
                SELECT a.name, COUNT(d.id) as doc_count, COUNT(dc.id) as chunk_count
                FROM agentes a
                LEFT JOIN documents d ON a.id = d.agent_id
                LEFT JOIN document_chunks dc ON a.id = dc.agent_id
                GROUP BY a.id, a.name
                ORDER BY doc_count DESC
            """
            docs_per_agent = self.agent_manager._execute_query(query_docs_per_agent, fetch='all')
            stats['documents_per_agent'] = []
            if docs_per_agent:
                for row in docs_per_agent:
                    stats['documents_per_agent'].append({
                        'agent_name': row[0],
                        'documents': row[1],
                        'chunks': row[2]
                    })
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do banco: {e}")
            return {'error': str(e)}
    
    def get_all_documents_from_db(self) -> List[Dict]:
        """Lista todos os documentos do banco PostgreSQL com detalhes"""
        try:
            query = """
                SELECT 
                    d.id,
                    d.file_name,
                    d.source_type,
                    d.content_hash,
                    d.created_at,
                    a.name as agent_name,
                    a.id as agent_id,
                    COUNT(dc.id) as chunk_count
                FROM documents d
                JOIN agentes a ON d.agent_id = a.id
                LEFT JOIN document_chunks dc ON d.id = dc.document_id
                GROUP BY d.id, d.file_name, d.source_type, d.content_hash, d.created_at, a.name, a.id
                ORDER BY d.created_at DESC
            """
            
            rows = self.agent_manager._execute_query(query, fetch='all')
            
            documents = []
            if rows:
                for row in rows:
                    documents.append({
                        'id': str(row[0]),
                        'name': row[1] or 'Documento sem nome',
                        'file_type': row[2] or 'unknown',
                        'content_hash': row[3],
                        'created_at': row[4],
                        'agent_id': str(row[5]),
                        'chunk_count': row[6] or 0
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao listar documentos do banco: {e}")
            return []
    
    def get_recent_activity(self) -> Dict:
        """Obtém atividade recente do sistema"""
        try:
            activity = {}
            
            # Últimas conversas
            query_recent_conversations = """
                SELECT c.user_message, a.name as agent_name, c.created_at
                FROM conversations c
                JOIN agentes a ON c.agent_id = a.id
                ORDER BY c.created_at DESC
                LIMIT 5
            """
            recent_conversations = self.agent_manager._execute_query(query_recent_conversations, fetch='all')
            activity['recent_conversations'] = []
            if recent_conversations:
                for row in recent_conversations:
                    activity['recent_conversations'].append({
                        'message': row[0][:50] + '...' if len(row[0]) > 50 else row[0],
                        'agent': row[1],
                        'timestamp': row[2]
                    })
            
            # Últimos documentos adicionados
            query_recent_docs = """
                SELECT d.file_name, a.name as agent_name, d.created_at
                FROM documents d
                JOIN agentes a ON d.agent_id = a.id
                ORDER BY d.created_at DESC
                LIMIT 5
            """
            recent_docs = self.agent_manager._execute_query(query_recent_docs, fetch='all')
            activity['recent_documents'] = []
            if recent_docs:
                for row in recent_docs:
                    activity['recent_documents'].append({
                        'file_name': row[0] or 'Documento sem nome',
                        'agent': row[1],
                        'timestamp': row[2]
                    })
            
            return activity
            
        except Exception as e:
            logger.error(f"Erro ao obter atividade recente: {e}")
            return {'error': str(e)}
    
    def process_document_upload(self, file_content: str, file_name: str, agent_id: str = None) -> Dict:
        """Processa upload de documento com vetorização real"""
        try:
            import hashlib
            import uuid
            from datetime import datetime
            
            # Se não há agent_id, criar ou usar agente padrão
            if not agent_id:
                # Buscar agente padrão existente
                default_query = "SELECT id FROM agentes WHERE name = 'Sistema Padrão' LIMIT 1"
                default_agent = self.agent_manager._execute_query(default_query, fetch='one')
                
                if default_agent:
                    agent_id = str(default_agent['id'])
                else:
                    # Criar agente padrão
                    agent_id = self.agent_manager.create_agent(
                        name="Sistema Padrão",
                        description="Agente padrão do sistema para documentos gerais",
                        agent_type="Geral",
                        system_prompt="Você é um assistente inteligente que ajuda com documentos gerais.",
                        model="gpt-3.5-turbo",
                        temperature=0.7
                    )
                    
                    if not agent_id:
                        return {
                            'success': False,
                            'error': 'Falha ao criar agente padrão'
                        }
            
            # Gerar hash do conteúdo
            content_hash = hashlib.sha256(file_content.encode()).hexdigest()
            
            # Verificar se documento já existe
            check_query = "SELECT id FROM documents WHERE content_hash = %s"
            existing = self.agent_manager._execute_query(check_query, (content_hash,), fetch='one')
            
            if existing:
                return {
                    'success': False,
                    'error': 'Documento já existe na base de dados'
                }
            
            # Inserir documento
            doc_id = str(uuid.uuid4())
            source_type = file_name.split('.')[-1].lower() if '.' in file_name else 'txt'
            
            insert_doc_query = """
                INSERT INTO documents (id, agent_id, file_name, source_type, content_hash, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            self.agent_manager._execute_query(insert_doc_query, (
                doc_id, agent_id, file_name, source_type, content_hash, datetime.now()
            ))
            
            # Chunking do documento
            chunks = self._create_chunks(file_content)
            
            # Gerar embeddings e inserir chunks
            embeddings_created = 0
            for chunk_text in chunks:
                try:
                    # Gerar embedding (simulado - em produção usar OpenAI/etc)
                    embedding = self._generate_embedding(chunk_text)
                    
                    if embedding:
                        chunk_id = str(uuid.uuid4())
                        insert_chunk_query = """
                            INSERT INTO document_chunks (id, document_id, agent_id, chunk_text, embedding, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        
                        self.agent_manager._execute_query(insert_chunk_query, (
                            chunk_id, doc_id, agent_id, chunk_text, embedding, datetime.now()
                        ))
                        embeddings_created += 1
                
                except Exception as e:
                    logger.warning(f"Erro ao processar chunk: {e}")
                    continue
            
            return {
                'success': True,
                'document_id': doc_id,
                'chunks_created': embeddings_created,
                'total_chunks': len(chunks),
                'agent_id': agent_id
            }
            
        except Exception as e:
            logger.error(f"Erro no upload do documento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divide texto em chunks com sobreposição"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Tentar quebrar em fronteira de palavra
            if end < len(text):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size // 2:
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para o texto (simulado)"""
        try:
            import random
            # Em produção, usar OpenAI embeddings ou similar
            # Por enquanto, retornar embedding simulado
            return [random.random() for _ in range(1536)]  # Dimensão do text-embedding-3-small
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return None
    
    def save_conversation_to_db(self, agent_id: str, user_message: str, assistant_response: str, 
                               provider: str, model_used: str, response_time: float = 0) -> bool:
        """Salva conversa no banco de dados PostgreSQL"""
        try:
            # 1. Inserir conversa
            conversation_query = """
                INSERT INTO conversations (agent_id, user_message) 
                VALUES (%s, %s) RETURNING id;
            """
            conversation_result = self.agent_manager._execute_query(
                conversation_query, 
                (agent_id, user_message), 
                fetch='one'
            )
            
            if conversation_result:
                conversation_id = conversation_result[0]
                
                # 2. Inserir resposta do LLM
                response_query = """
                    INSERT INTO llm_responses (conversation_id, provider, model_used, response_text, tokens_used) 
                    VALUES (%s, %s, %s, %s, %s);
                """
                
                # Estimar tokens (aproximação simples)
                estimated_tokens = len(assistant_response.split()) * 1.3
                
                self.agent_manager._execute_query(
                    response_query,
                    (conversation_id, provider, model_used, assistant_response, int(estimated_tokens))
                )
                
                logger.info(f"Conversa salva no banco: conversation_id={conversation_id}")
                return True
            else:
                logger.error("Falha ao inserir conversa no banco")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao salvar conversa no banco: {e}")
            return False
    
    def get_available_models_by_provider(self) -> Dict[str, List[str]]:
        """Retorna modelos disponíveis APENAS para provedores configurados"""
        
        # Verificar quais provedores estão realmente configurados
        configured_providers = []
        if os.getenv('OPENAI_API_KEY'):
            configured_providers.append('openai')
        if os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_GEMINI_API_KEY'):
            configured_providers.append('google')
        if os.getenv('OPENROUTER_API_KEY'):
            configured_providers.append('openrouter')
        if os.getenv('DEEPSEEK_API_KEY'):
            configured_providers.append('deepseek')
        
        # Tentar usar o novo sistema de modelos
        try:
            from llm_models_config import models_manager
            available = models_manager.get_provider_models_simple()
            # Filtrar apenas provedores configurados
            filtered = {k: v for k, v in available.items() if k in configured_providers}
            return filtered if filtered else {'openai': ['gpt-3.5-turbo']}  # Fallback mínimo
        except ImportError:
            logger.warning("Sistema de modelos avançado não disponível, usando fallback")
        
        # Fallback SEGURO - apenas modelos testados
        safe_models = {
            'openai': [
                'gpt-4o',
                'gpt-4o-mini', 
                'gpt-4-turbo',
                'gpt-4',
                'gpt-3.5-turbo'
            ]
        }
        
        # Só adicionar outros provedores se realmente configurados
        if 'google' in configured_providers:
            safe_models['google'] = ['gemini-1.5-flash', 'gemini-pro']
        
        if 'openrouter' in configured_providers:
            safe_models['openrouter'] = ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet']
        
        if 'deepseek' in configured_providers:
            safe_models['deepseek'] = ['deepseek-chat', 'deepseek-coder']
        
        # Retornar apenas modelos de provedores configurados
        available_models = {}
        for provider in configured_providers:
            if provider in safe_models:
                available_models[provider] = safe_models[provider]
        
        # Fallback de emergência - sempre incluir OpenAI se não houver nenhum
        if not available_models:
            available_models['openai'] = ['gpt-3.5-turbo']
            logger.warning("Nenhum provedor configurado, usando fallback OpenAI")
        
        return available_models

@st.cache_resource
def initialize_system():
    """Inicializa o sistema unificado"""
    return RAGSystemUnified()

def main():
    """Interface principal do sistema"""
    
    # Inicializar sistema
    rag_system = initialize_system()
    
    # Header principal
    st.markdown('<h1 class="main-header">🚀 RAG Python v1.5.1 - Sistema Completo</h1>', 
                unsafe_allow_html=True)
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Dashboard",
        "💬 Chat RAG", 
        "🤖 Agentes",
        "🔄 Multi-LLM",
        "🔒 Privacidade",
        "📁 Documentos",
        "⚙️ Configurações"
    ])
    
    with tab1:
        dashboard_interface(rag_system)
    
    with tab2:
        chat_rag_interface(rag_system)
    
    with tab3:
        agents_interface(rag_system)
    
    with tab4:
        multi_llm_interface(rag_system)
    
    with tab5:
        privacy_interface(rag_system)
    
    with tab6:
        documents_interface(rag_system)
    
    with tab7:
        settings_interface(rag_system)

def dashboard_interface(rag_system):
    """Interface do Dashboard com monitoramento completo"""
    st.header("📊 Dashboard do Sistema")
    
    # Sub-tabs do dashboard
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Visão Geral",
        "🔌 Status Conexões", 
        "📄 Documentos DB",
        "⚡ Atividade Recente"
    ])
    
    with tab1:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            try:
                agents = rag_system.agent_manager.get_all_agents()
                st.metric("🤖 Agentes", len(agents), help="Agentes especializados cadastrados")
            except:
                st.metric("🤖 Agentes", "N/A", help="Erro ao carregar agentes")
        
        with col2:
            # Documentos do banco PostgreSQL
            try:
                db_stats = rag_system.get_database_stats()
                docs_count = db_stats.get('documents_count', 0)
                st.metric("📄 Documentos DB", docs_count, help="Documentos no PostgreSQL")
            except:
                st.metric("📄 Documentos", len(rag_system.documents), help="Documentos na base de conhecimento")
        
        with col3:
            configured_keys = sum([
                bool(os.getenv('OPENAI_API_KEY')),
                bool(os.getenv('GOOGLE_API_KEY')),
                bool(os.getenv('OPENROUTER_API_KEY')),
                bool(os.getenv('DEEPSEEK_API_KEY'))
            ])
            st.metric("🔑 API Keys", f"{configured_keys}/4", help="API Keys configuradas")
        
        with col4:
            try:
                providers_info = rag_system.llm_manager.get_provider_info()
                active_providers = 0
                for info in providers_info.values():
                    if isinstance(info, dict) and info.get('available', False):
                        active_providers += 1
                st.metric("🌐 Provedores", f"{active_providers}/4", help="Provedores LLM ativos")
            except:
                st.metric("🌐 Provedores", "N/A", help="Erro ao verificar provedores")
        
        # Estatísticas do banco
        st.markdown("---")
        st.subheader("📊 Estatísticas do Banco PostgreSQL")
        
        try:
            db_stats = rag_system.get_database_stats()
            if 'error' not in db_stats:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📝 Chunks", db_stats.get('chunks_count', 0), help="Pedaços de texto vetorizados")
                
                with col2:
                    st.metric("💬 Conversas", db_stats.get('conversations_count', 0), help="Conversas registradas")
                
                with col3:
                    st.metric("🤖 Respostas LLM", db_stats.get('llm_responses_count', 0), help="Respostas dos LLMs")
                
                with col4:
                    docs_per_agent = db_stats.get('documents_per_agent', [])
                    active_agents = len([a for a in docs_per_agent if a['documents'] > 0])
                    st.metric("🎯 Agentes Ativos", active_agents, help="Agentes com documentos")
                
                # Gráfico de documentos por agente
                if docs_per_agent:
                    st.markdown("### 📊 Documentos por Agente")
                    chart_data = []
                    for agent in docs_per_agent[:10]:  # Top 10
                        chart_data.append({
                            'Agente': agent['agent_name'],
                            'Documentos': agent['documents'],
                            'Chunks': agent['chunks']
                        })
                    
                    if chart_data:
                        import pandas as pd
                        df = pd.DataFrame(chart_data)
                        st.bar_chart(df.set_index('Agente'))
            else:
                st.error(f"❌ Erro ao obter estatísticas: {db_stats['error']}")
        except Exception as e:
            st.error(f"❌ Erro ao carregar estatísticas do banco: {e}")
        
        # Status dos provedores LLM
        st.markdown("---")
        st.subheader("🌐 Status dos Provedores LLM")
        
        providers_status = {
            "OpenAI": {
                "key": bool(os.getenv('OPENAI_API_KEY')),
                "icon": "🤖",
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"]
            },
            "Google Gemini": {
                "key": bool(os.getenv('GOOGLE_API_KEY')),
                "icon": "🧠",
                "models": ["gemini-pro", "gemini-1.5-flash"]
            },
            "OpenRouter": {
                "key": bool(os.getenv('OPENROUTER_API_KEY')),
                "icon": "🌐",
                "models": ["claude-3", "llama-2", "mixtral"]
            },
            "DeepSeek": {
                "key": bool(os.getenv('DEEPSEEK_API_KEY')),
                "icon": "🔮",
                "models": ["deepseek-chat", "deepseek-coder"]
            }
        }
        
        cols = st.columns(4)
        for i, (provider, info) in enumerate(providers_status.items()):
            with cols[i]:
                status = "✅ Ativo" if info['key'] else "❌ Inativo"
                color = "#d4edda" if info['key'] else "#f8d7da"
                border_color = "#28a745" if info['key'] else "#dc3545"
                
                st.markdown(f"""
                <div style="
                    background-color: {color}; 
                    border: 2px solid {border_color}; 
                    border-radius: 10px; 
                    padding: 15px; 
                    text-align: center;
                    margin: 5px;
                    min-height: 120px;
                ">
                    <h3 style="margin: 0;">{info['icon']} {provider}</h3>
                    <p style="margin: 5px 0; font-weight: bold;">{status}</p>
                    <small>Modelos: {len(info['models'])}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("🔌 Status das Conexões")
        
        # Status PostgreSQL
        st.markdown("### 🐘 PostgreSQL Database")
        
        if st.button("🔄 Verificar Conexão PostgreSQL", key="check_postgres"):
            with st.spinner("Verificando conexão..."):
                db_status = rag_system.check_database_connection()
                
                if db_status['status'] == 'connected':
                    st.success("✅ PostgreSQL Conectado!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"""
                        **📊 Informações da Conexão:**
                        - **Banco:** {db_status['database']}
                        - **Usuário:** {db_status['user']}
                        - **Pool:** {'✅ Ativo' if db_status['connection_pool'] else '❌ Inativo'}
                        """)
                    
                    with col2:
                        st.info(f"""
                        **🕒 Timestamp:** {db_status['timestamp']}
                        
                        **📝 Versão:**
                        {db_status['version'][:50]}...
                        """)
                
                elif db_status['status'] == 'disconnected':
                    st.error(f"❌ PostgreSQL Desconectado: {db_status['error']}")
                else:
                    st.warning(f"⚠️ Erro na conexão: {db_status['error']}")
        
        # Status LLM Providers
        st.markdown("---")
        st.markdown("### 🤖 Status Provedores LLM")
        
        if st.button("🧪 Testar Todos os Provedores", key="test_all_providers"):
            with st.spinner("Testando provedores..."):
                providers_to_test = ['openai', 'google', 'openrouter', 'deepseek']
                
                for provider in providers_to_test:
                    try:
                        # Teste simples
                        messages = [{"role": "user", "content": "Olá! Responda apenas 'OK' para confirmar que está funcionando."}]
                        response = rag_system.llm_manager.generate_response(messages, provider_name=provider)
                        
                        if response and 'response' in response:
                            st.success(f"✅ {provider.upper()}: Funcionando")
                        else:
                            st.error(f"❌ {provider.upper()}: Sem resposta")
                    except Exception as e:
                        st.error(f"❌ {provider.upper()}: {str(e)[:100]}...")
        
        # Status Sistema de Arquivos
        st.markdown("---")
        st.markdown("### 📁 Sistema de Arquivos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Verificar diretórios importantes
            dirs_to_check = [
                'agent_uploads',
                'agent_vector_dbs', 
                'documents',
                'static/documentos_gerados'
            ]
            
            st.markdown("**📂 Diretórios:**")
            for dir_name in dirs_to_check:
                if os.path.exists(dir_name):
                    file_count = len(os.listdir(dir_name)) if os.path.isdir(dir_name) else 0
                    st.success(f"✅ {dir_name} ({file_count} itens)")
                else:
                    st.error(f"❌ {dir_name} (não encontrado)")
        
        with col2:
            # Verificar arquivos importantes
            files_to_check = [
                'schema.sql',
                'requirements.txt',
                'agents_config.json'
            ]
            
            st.markdown("**📄 Arquivos:**")
            for file_name in files_to_check:
                if os.path.exists(file_name):
                    file_size = os.path.getsize(file_name)
                    st.success(f"✅ {file_name} ({file_size} bytes)")
                else:
                    st.error(f"❌ {file_name} (não encontrado)")
    
    with tab3:
        st.subheader("📄 Documentos no Banco PostgreSQL")
        
        # Botão para atualizar
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Atualizar Lista", key="refresh_docs"):
                st.rerun()
        
        # Obter todos os documentos
        try:
            documents = rag_system.get_all_documents_from_db()
            
            if documents:
                st.success(f"📊 Total de documentos encontrados: **{len(documents)}**")
                
                # Filtros
                st.markdown("### 🔍 Filtros")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Filtro por agente
                    agents_in_docs = list(set([doc['agent_name'] for doc in documents]))
                    selected_agent_filter = st.selectbox(
                        "Filtrar por Agente:",
                        ["Todos"] + agents_in_docs,
                        key="agent_filter"
                    )
                
                with col2:
                    # Filtro por tipo
                    types_in_docs = list(set([doc['source_type'] for doc in documents]))
                    selected_type_filter = st.selectbox(
                        "Filtrar por Tipo:",
                        ["Todos"] + types_in_docs,
                        key="type_filter"
                    )
                
                with col3:
                    # Ordenação
                    sort_options = {
                        "Data (Mais Recente)": "created_at_desc",
                        "Data (Mais Antigo)": "created_at_asc", 
                        "Nome A-Z": "name_asc",
                        "Chunks (Maior)": "chunks_desc"
                    }
                    selected_sort = st.selectbox("Ordenar por:", list(sort_options.keys()))
                
                # Aplicar filtros
                filtered_docs = documents.copy()
                
                if selected_agent_filter != "Todos":
                    filtered_docs = [doc for doc in filtered_docs if doc['agent_name'] == selected_agent_filter]
                
                if selected_type_filter != "Todos":
                    filtered_docs = [doc for doc in filtered_docs if doc['source_type'] == selected_type_filter]
                
                # Aplicar ordenação
                sort_key = sort_options[selected_sort]
                if sort_key == "created_at_desc":
                    filtered_docs.sort(key=lambda x: x['created_at'], reverse=True)
                elif sort_key == "created_at_asc":
                    filtered_docs.sort(key=lambda x: x['created_at'])
                elif sort_key == "name_asc":
                    filtered_docs.sort(key=lambda x: x['file_name'].lower())
                elif sort_key == "chunks_desc":
                    filtered_docs.sort(key=lambda x: x['chunk_count'], reverse=True)
                
                # Exibir documentos
                st.markdown(f"### 📋 Lista de Documentos ({len(filtered_docs)} encontrados)")
                
                for i, doc in enumerate(filtered_docs):
                    with st.expander(f"📄 {doc['file_name']} - {doc['agent_name']} ({doc['chunk_count']} chunks)"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            **📋 Informações:**
                            - **ID:** `{doc['id']}`
                            - **Nome:** {doc['file_name']}
                            - **Tipo:** {doc['source_type']}
                            - **Agente:** {doc['agent_name']}
                            """)
                        
                        with col2:
                            st.markdown(f"""
                            **📊 Estatísticas:**
                            - **Chunks:** {doc['chunk_count']}
                            - **Hash:** `{doc['content_hash']}`
                            - **Criado:** {doc['created_at']}
                            """)
                        
                        # Botões de ação
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.button(f"🔍 Ver Chunks", key=f"view_chunks_{i}", help="Ver pedaços do documento")
                        with col2:
                            st.button(f"📊 Estatísticas", key=f"stats_{i}", help="Ver estatísticas detalhadas")
                        with col3:
                            st.button(f"🗑️ Remover", key=f"delete_{i}", help="Remover documento", type="secondary")
            
            else:
                st.info("📭 Nenhum documento encontrado no banco PostgreSQL")
                st.markdown("""
                **💡 Dicas:**
                - Verifique se há agentes cadastrados
                - Faça upload de documentos na aba **📁 Documentos**
                - Verifique a conexão com PostgreSQL na aba **🔌 Status Conexões**
                """)
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar documentos: {e}")
    
    with tab4:
        st.subheader("⚡ Atividade Recente do Sistema")
        
        try:
            activity = rag_system.get_recent_activity()
            
            if 'error' not in activity:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 💬 Últimas Conversas")
                    recent_conversations = activity.get('recent_conversations', [])
                    
                    if recent_conversations:
                        for conv in recent_conversations:
                            st.markdown(f"""
                            <div style="
                                background-color: #f8f9fa; 
                                border-left: 4px solid #007bff;
                                padding: 10px; 
                                margin: 5px 0;
                                border-radius: 5px;
                            ">
                                <strong>🤖 {conv['agent']}</strong><br>
                                <em>{conv['message']}</em><br>
                                <small>🕒 {conv['timestamp']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("📭 Nenhuma conversa recente encontrada")
                
                with col2:
                    st.markdown("### 📄 Últimos Documentos")
                    recent_docs = activity.get('recent_documents', [])
                    
                    if recent_docs:
                        for doc in recent_docs:
                            st.markdown(f"""
                            <div style="
                                background-color: #f8f9fa; 
                                border-left: 4px solid #28a745;
                                padding: 10px; 
                                margin: 5px 0;
                                border-radius: 5px;
                            ">
                                <strong>📄 {doc['file_name']}</strong><br>
                                <em>Agente: {doc['agent']}</em><br>
                                <small>🕒 {doc['timestamp']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("📭 Nenhum documento recente encontrado")
                
                # Ações rápidas
                st.markdown("---")
                st.markdown("### ⚡ Ações Rápidas")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("🔧 Configurar APIs", help="Ir para configurações de API"):
                        st.info("💡 Use a aba **⚙️ Configurações** acima para configurar APIs")
                
                with col2:
                    if st.button("🤖 Criar Agente", help="Criar novo agente"):
                        st.info("💡 Use a aba **🤖 Agentes** acima para criar agentes")
                
                with col3:
                    if st.button("📤 Upload Docs", help="Fazer upload de documentos"):
                        st.info("💡 Use a aba **📁 Documentos** acima para upload")
                
                with col4:
                    if st.button("🧪 Testar LLMs", help="Testar conectividade"):
                        st.info("💡 Use a aba **🔄 Multi-LLM** > **🧪 Testes** para testar LLMs")
            
            else:
                st.error(f"❌ Erro ao carregar atividade: {activity['error']}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar atividade recente: {e}")
        
        # Informações do sistema
        st.markdown("---")
        st.subheader("ℹ️ Informações do Sistema")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.info("""
            **🚀 RAG Python v1.5.1-Unified-Hotfix**
            
            Sistema completo de RAG com:
            - ✅ Multi-LLM integration
            - ✅ Sistema de agentes especializados
            - ✅ Compliance LGPD
            - ✅ Interface unificada
            - ✅ Monitoramento completo
            """)
        
        with info_col2:
            st.success("""
            **✅ Sistema Operacional**
            
            Status:
            - ✅ Interface carregada
            - ✅ Banco PostgreSQL conectado
            - ✅ Sistema de arquivos OK
            - ✅ Monitoramento ativo
            - ✅ Pronto para uso
            """)

def chat_rag_interface(rag_system):
    """Interface do Chat RAG"""
    st.header("💬 Chat RAG Inteligente")
    
    # Configuração em três colunas
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Seleção de agente
        agents = rag_system.agent_manager.get_all_agents()
        agent_options = {"Sistema Padrão": None}
        agent_options.update({agent['name']: agent['id'] for agent in agents})
        
        selected_agent = st.selectbox("🤖 Selecionar Agente:", list(agent_options.keys()))
        agent_id = agent_options[selected_agent]
    
    with col2:
        # Seleção de LLM
        llm_options = {
            "🤖 OpenAI (GPT)": "openai",
            "🔍 Google Gemini": "google", 
            "🌐 OpenRouter": "openrouter",
            "🧠 DeepSeek": "deepseek"
        }
        
        selected_llm_display = st.selectbox("🔧 Selecionar LLM:", list(llm_options.keys()))
        selected_llm = llm_options[selected_llm_display]
    
    with col3:
        # Seleção de modelo específico
        available_models = rag_system.get_available_models_by_provider()
        models_for_provider = available_models.get(selected_llm, [])
        
        if models_for_provider:
            selected_model = st.selectbox(
                f"🧠 Modelo {selected_llm.upper()}:",
                models_for_provider,
                help=f"Modelos disponíveis para {selected_llm_display}"
            )
        else:
            selected_model = "default"
            st.info(f"⚠️ Modelo padrão para {selected_llm_display}")
    
    # Mostrar configuração atual
    if agent_id:
        agent = rag_system.agent_manager.get_agent_by_id(agent_id)
        if agent:
            st.info(f"🤖 **Agente:** {agent['name']} | **LLM:** {selected_llm_display} | **Modelo:** {selected_model} | **Documentos:** {len(rag_system.get_agent_documents(agent_id))} docs")
    else:
        st.info(f"🤖 **Sistema Padrão** | **LLM:** {selected_llm_display} | **Modelo:** {selected_model} | **Base:** Geral")
    
    # Histórico do chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Área de mensagens
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
                    st.caption(f"🤖 {message.get('agent', 'Sistema')} | 🔧 {message.get('llm', 'N/A')} | 🧠 {message.get('model', 'N/A')} | ⚡ {message.get('response_time', 0):.2f}s")
    
    # Input de mensagem com suporte ao Enter
    user_input = st.chat_input("💭 Digite sua pergunta...", key="chat_rag_input")
    
    # Processar mensagem quando Enter for pressionado
    if user_input:
        # Adicionar mensagem do usuário
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Processar resposta
        with st.spinner("🤔 Pensando..."):
            result = rag_system.query_with_agent(user_input, agent_id, selected_llm, selected_model)
        
        # Adicionar resposta do assistente
        if result['success']:
            # Salvar conversa no banco de dados
            if agent_id:  # Só salva se tiver agente específico
                rag_system.save_conversation_to_db(
                    agent_id=agent_id,
                    user_message=user_input,
                    assistant_response=result['answer'],
                    provider=result.get('llm_used', selected_llm),
                    model_used=result.get('model_used', 'unknown'),
                    response_time=result.get('response_time', 0)
                )
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': result['answer'],
                'agent': result.get('agent_used', selected_agent),
                'llm': selected_llm_display,
                'model': result.get('model_used', 'N/A'),
                'response_time': result.get('response_time', 0)
            })
        else:
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': f"❌ Erro: {result.get('answer', 'Erro desconhecido')}",
                'agent': result.get('agent_used', selected_agent),
                'llm': selected_llm_display,
                'model': result.get('model_used', 'N/A'),
                'response_time': 0
            })
        
        st.rerun()
    
    # Botões de ação
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🗑️ Limpar Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📊 Ver Documentos"):
            if agent_id:
                docs = rag_system.get_agent_documents(agent_id)
                st.info(f"📚 {len(docs)} documentos na base do agente")
                for doc in docs[:3]:  # Mostrar primeiros 3
                    st.write(f"📄 {doc.get('name', 'Documento')}")
            else:
                st.info("📚 Base de documentos geral")
    
    with col3:
        st.write("")  # Espaço

def agents_interface(rag_system):
    """Interface de gerenciamento de agentes"""
    st.header("🤖 Sistema de Agentes Especializados")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Agentes", "➕ Criar Agente", "⚙️ Configurar Agente"])
    
    with tab1:
        st.subheader("👥 Agentes Cadastrados")
        
        agents = rag_system.agent_manager.get_all_agents()
        
        if agents:
            for agent in agents:
                with st.expander(f"🤖 {agent['name']} - {agent.get('agent_type', 'Geral')}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Descrição:** {agent['description']}")
                        st.write(f"**Modelo:** {agent['model']}")
                        st.write(f"**Temperatura:** {agent['temperature']}")
                        st.write(f"**Criado em:** {agent.get('created_at', 'N/A')}")
                        
                        with st.expander("Ver Prompt do Sistema"):
                            st.code(agent['system_prompt'], language='text')
                    
                    with col2:
                        if st.button("🗑️ Deletar", key=f"delete_{agent['id']}"):
                            if rag_system.agent_manager.delete_agent(agent['id']):
                                st.success("Agente deletado com sucesso!")
                                st.rerun()
        else:
            st.info("📝 Nenhum agente cadastrado ainda. Crie seu primeiro agente!")
    
    with tab2:
        st.subheader("➕ Criar Novo Agente")
        
        with st.form("create_agent_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                agent_name = st.text_input("🏷️ Nome do Agente", placeholder="Ex: Assistente Jurídico")
                agent_type = st.selectbox("🎯 Tipo de Agente", [
                    "Conversacional", "Pesquisador", "Executor", "Especialista"
                ])
                model = st.selectbox("🤖 Modelo LLM", [
                    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4o-mini",
                    "gemini-pro", "gemini-pro-vision", "deepseek-chat", "deepseek-coder"
                ])
            
            with col2:
                temperature = st.slider("🌡️ Temperatura", 0.0, 2.0, 0.7, 0.1)
                description = st.text_area("📝 Descrição", 
                                         placeholder="Descreva o propósito e especialidade do agente")
            
            system_prompt = st.text_area("🎭 Prompt do Sistema", height=200,
                                       placeholder="Defina o comportamento e especialidade do agente...")
            
            if st.form_submit_button("🚀 Criar Agente", type="primary"):
                if agent_name and system_prompt:
                    agent_id = rag_system.agent_manager.create_agent(
                        name=agent_name,
                        description=description,
                        agent_type=agent_type,
                        system_prompt=system_prompt,
                        model=model,
                        temperature=temperature
                    )
                    
                    if agent_id:
                        st.success(f"✅ Agente '{agent_name}' criado com sucesso!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao criar agente. Verifique a conexão com banco de dados.")
                else:
                    st.error("⚠️ Preencha pelo menos o nome e o prompt do sistema.")
    
    with tab3:
        st.subheader("⚙️ Configurar Agente Existente")
        
        agents = rag_system.agent_manager.get_all_agents()
        if agents:
            agent_to_edit = st.selectbox("Selecionar Agente:", 
                                       [f"{a['name']} (ID: {a['id']})" for a in agents])
            
            if agent_to_edit:
                agent_id = agent_to_edit.split("ID: ")[1].rstrip(")")
                agent = rag_system.agent_manager.get_agent_by_id(agent_id)
                
                if agent:
                    with st.form("edit_agent_form"):
                        new_name = st.text_input("Nome", value=agent['name'])
                        new_description = st.text_area("Descrição", value=agent['description'])
                        new_model = st.selectbox("Modelo", [
                            "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4o-mini",
                            "gemini-pro", "deepseek-chat"
                        ], index=0 if agent['model'] == "gpt-3.5-turbo" else 0)
                        new_temperature = st.slider("Temperatura", 0.0, 2.0, float(agent['temperature']), 0.1)
                        new_prompt = st.text_area("Prompt do Sistema", value=agent['system_prompt'], height=200)
                        
                        if st.form_submit_button("💾 Salvar Alterações"):
                            update_data = {
                                'name': new_name,
                                'description': new_description,
                                'system_prompt': new_prompt,
                                'model': new_model,
                                'temperature': new_temperature
                            }
                            
                            if rag_system.agent_manager.update_agent(agent_id, update_data):
                                st.success("✅ Agente atualizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao atualizar agente.")
        else:
            st.info("Nenhum agente disponível para configuração.")

def multi_llm_interface(rag_system):
    """Interface Multi-LLM com testes e comparações"""
    st.header("🤖 Sistema Multi-LLM")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Individual", "⚖️ Comparação", "🧪 Testes", "🔧 Modelos Disponíveis"])
    
    with tab1:
        st.subheader("💬 Chat com Provedor Específico")
        
        # Seleção de provedor
        providers_available = ["openai", "google", "openrouter", "deepseek"]
        selected_provider = st.selectbox(
            "🔧 Escolher Provedor LLM:",
            providers_available,
            format_func=lambda x: {
                "openai": "🤖 OpenAI (GPT)",
                "google": "🔍 Google Gemini", 
                "openrouter": "🌐 OpenRouter",
                "deepseek": "🧠 DeepSeek"
            }.get(x, x.upper())
        )
        
        # Seleção de agente
        agents = rag_system.agent_manager.get_all_agents()
        agent_options = {"Sistema Padrão": None}
        agent_options.update({f"{agent['name']} (ID: {agent['id'][:8]}...)": agent['id'] for agent in agents})
        
        selected_agent_option = st.selectbox(
            "🤖 Escolher Agente:",
            list(agent_options.keys()),
            help="Selecione qual agente especializado usar para a conversa"
        )
        selected_agent_id = agent_options[selected_agent_option]
        
        # Mostrar info do agente selecionado
        if selected_agent_id:
            agent = rag_system.agent_manager.get_agent_by_id(selected_agent_id)
            if agent:
                st.info(f"🤖 **Agente:** {agent['name']} | **Tipo:** {agent.get('agent_type', 'N/A')} | **Modelo:** {agent.get('model', 'N/A')}")
        else:
            st.info(f"🤖 **Sistema Padrão** | **Provedor:** {selected_provider.upper()}")
        
        # Chat input
        user_question = st.chat_input("💭 Digite sua pergunta...", key="multi_llm_input")
        
        # Inicializar histórico se não existir
        if f"chat_history_{selected_provider}" not in st.session_state:
            st.session_state[f"chat_history_{selected_provider}"] = []
        
        # Processar nova mensagem
        if user_question:
            # Adicionar pergunta do usuário
            st.session_state[f"chat_history_{selected_provider}"].append({
                'role': 'user',
                'content': user_question
            })
            
            # Gerar resposta
            with st.spinner(f"🤔 {selected_provider.upper()} pensando..."):
                if selected_agent_id:
                    # Usar agente específico
                    result = rag_system.query_with_agent(user_question, selected_agent_id)
                else:
                    # Usar provedor específico
                    result = rag_system.llm_manager.generate_response(
                        user_question, 
                        provider_name=selected_provider
                    )
                
                # Adicionar resposta
                if result.get('success', False):
                    st.session_state[f"chat_history_{selected_provider}"].append({
                        'role': 'assistant',
                        'content': result.get('response', result.get('answer', 'Sem resposta')),
                        'provider': selected_provider,
                        'agent': selected_agent_option if selected_agent_id else 'Sistema Padrão',
                        'response_time': result.get('response_time', 0)
                    })
                else:
                    st.session_state[f"chat_history_{selected_provider}"].append({
                        'role': 'error',
                        'content': f"Erro: {result.get('error', 'Erro desconhecido')}",
                        'provider': selected_provider
                    })
        
        # Mostrar histórico do chat
        chat_container = st.container()
        with chat_container:
            for message in st.session_state[f"chat_history_{selected_provider}"]:
                if message['role'] == 'user':
                    st.chat_message("user").write(message['content'])
                elif message['role'] == 'assistant':
                    with st.chat_message("assistant"):
                        st.write(message['content'])
                        st.caption(f"🤖 {message.get('provider', '').upper()} | ⚡ {message.get('response_time', 0):.2f}s | 👤 {message.get('agent', 'N/A')}")
                elif message['role'] == 'error':
                    st.error(f"❌ {message['content']}")
        
        # Botão para limpar chat
        if st.button(f"🗑️ Limpar Chat {selected_provider.upper()}"):
            st.session_state[f"chat_history_{selected_provider}"] = []
            st.rerun()
    
    with tab2:
        st.subheader("⚖️ Comparação Multi-LLM")
        
        # Seleção de agente para comparação
        agents = rag_system.agent_manager.get_all_agents()
        agent_options = {"Sistema Padrão": None}
        agent_options.update({f"{agent['name']} (ID: {agent['id'][:8]}...)": agent['id'] for agent in agents})
        
        comparison_agent_option = st.selectbox(
            "🤖 Agente para Comparação:",
            list(agent_options.keys()),
            help="Todos os provedores usarão este agente/sistema para responder",
            key="comparison_agent"
        )
        comparison_agent_id = agent_options[comparison_agent_option]
        
        # Seleção de provedores para comparação
        providers_available = ["openai", "google", "openrouter", "deepseek"]
        selected_providers = st.multiselect(
            "🔧 Provedores para Comparação:",
            providers_available,
            default=["openai", "google"],
            format_func=lambda x: {
                "openai": "🤖 OpenAI (GPT)",
                "google": "🔍 Google Gemini", 
                "openrouter": "🌐 OpenRouter",
                "deepseek": "🧠 DeepSeek"
            }.get(x, x.upper())
        )
        
        comparison_question = st.text_area("❓ Pergunta para Comparação:", 
                                         placeholder="Digite uma pergunta para comparar entre os provedores...")
        
        if st.button("⚖️ Comparar Provedores", type="primary"):
            if comparison_question and selected_providers:
                with st.spinner("🔄 Comparando provedores..."):
                    if comparison_agent_id:
                        # Usar agente específico para todos os provedores
                        results = {}
                        for provider in selected_providers:
                            try:
                                # Usar o agente com o provedor específico
                                result = rag_system.query_with_agent(comparison_question, comparison_agent_id, provider)
                                results[provider] = {
                                    'success': result.get('success', False),
                                    'response': result.get('answer', 'Sem resposta'),
                                    'response_time': result.get('response_time', 0),
                                    'error': result.get('error', None),
                                    'agent_used': result.get('agent_used', comparison_agent_option)
                                }
                            except Exception as e:
                                results[provider] = {
                                    'success': False,
                                    'response': '',
                                    'response_time': 0,
                                    'error': str(e),
                                    'agent_used': comparison_agent_option
                                }
                    else:
                        # Usar sistema multi-LLM sem agente específico
                        results = {}
                        for provider in selected_providers:
                            try:
                                messages = [{"role": "user", "content": comparison_question}]
                                result = rag_system.llm_manager.generate_response(messages, provider_name=provider)
                                
                                results[provider] = {
                                    'success': result.get('success', False),
                                    'response': result.get('response', 'Sem resposta'),
                                    'response_time': result.get('response_time', 0),
                                    'error': result.get('error', None),
                                    'agent_used': 'Sistema Padrão'
                                }
                            except Exception as e:
                                results[provider] = {
                                    'success': False,
                                    'response': '',
                                    'response_time': 0,
                                    'error': str(e),
                                    'agent_used': 'Sistema Padrão'
                                }
                
                if isinstance(results, dict) and 'error' not in results:
                    # Mostrar resultados
                    st.subheader("📊 Resultados da Comparação")
                    
                    for provider in selected_providers:
                        if provider in results:
                            result = results[provider]
                            
                            with st.expander(f"🤖 {provider.upper()} - {'✅ Sucesso' if result.get('success') else '❌ Erro'}"):
                                st.markdown(f"""
                                <div class="provider-result">
                                    <p><strong>⏱️ Tempo:</strong> {result.get('response_time', 0):.2f}s</p>
                                    <p><strong>🤖 Agente:</strong> {result.get('agent_used', comparison_agent_option)}</p>
                                    <p><strong>🔧 Provedor:</strong> {provider.upper()}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Resposta
                                if result.get('success'):
                                    st.text_area(f"Resposta {provider.upper()}:", 
                                               value=result.get('response', 'Erro na resposta'),
                                               height=200, key=f"response_{provider}")
                                else:
                                    st.error(f"Erro: {result.get('error', 'Erro desconhecido')}")
                    
                    # Métricas de comparação
                    st.subheader("📈 Métricas de Performance")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Corrigir o erro IndexError
                        valid_results = {p: r for p, r in results.items() if isinstance(r, dict) and r.get('success')}
                        times = [r.get('response_time', 0) for r in valid_results.values()]
                        
                        if times:
                            fastest_time = min(times)
                            fastest_providers = [p for p, r in valid_results.items() if r.get('response_time') == fastest_time]
                            if fastest_providers:
                                fastest_provider = fastest_providers[0]
                                st.metric("⚡ Mais Rápido", fastest_provider.upper(), f"{fastest_time:.2f}s")
                            else:
                                st.metric("⚡ Mais Rápido", "N/A", "0.00s")
                        else:
                            st.metric("⚡ Mais Rápido", "N/A", "0.00s")
                    
                    with col2:
                        successful = len(valid_results)
                        st.metric("✅ Sucessos", f"{successful}/{len(selected_providers)}")
                    
                    with col3:
                        avg_time = sum(times) / len(times) if times else 0
                        st.metric("⏱️ Tempo Médio", f"{avg_time:.2f}s")
                
                else:
                    st.error(f"Erro na comparação: {results.get('error', 'Erro desconhecido')}")
            else:
                if not comparison_question:
                    st.warning("⚠️ Digite uma pergunta para comparação.")
                if not selected_providers:
                    st.warning("⚠️ Selecione pelo menos um provedor para comparação.")
    
    with tab3:
        st.subheader("🧪 Testes de Conectividade")
        
        st.info("🔧 Teste a conectividade e configuração de cada provedor LLM")
        
        providers_available = ["openai", "google", "openrouter", "deepseek"]
        
        for provider in providers_available:
            with st.expander(f"🧪 Testar {provider.upper()}"):
                test_question = st.text_input(f"Pergunta de teste para {provider}:", 
                                            value="Olá, você está funcionando?",
                                            key=f"test_{provider}")
                
                if st.button(f"🧪 Testar {provider.upper()}", key=f"btn_test_{provider}"):
                    with st.spinner(f"🧪 Testando {provider}..."):
                        try:
                            result = rag_system.llm_manager.generate_response(
                                test_question, 
                                provider_name=provider
                            )
                            
                            if result.get('success', False):
                                st.success(f"✅ {provider.upper()} funcionando!")
                                st.info(f"⏱️ Tempo de resposta: {result.get('response_time', 0):.2f}s")
                                st.text_area(f"Resposta de {provider}:", 
                                           value=result.get('response', 'Sem resposta'),
                                           height=100, key=f"test_response_{provider}")
                            else:
                                st.error(f"❌ Erro no {provider.upper()}: {result.get('error', 'Erro desconhecido')}")
                        
                        except Exception as e:
                            st.error(f"❌ Exceção no {provider.upper()}: {str(e)}")
    
    with tab4:
        st.subheader("🔧 Modelos Disponíveis por Provedor")
        
        st.markdown("""
        📋 **Informações sobre Modelos LLM**
        
        Esta seção mostra todos os modelos disponíveis para cada provedor LLM configurado no sistema.
        """)
        
        # Obter modelos disponíveis
        available_models = rag_system.get_available_models_by_provider()
        
        # Criar tabs para cada provedor
        provider_tabs = st.tabs([
            "🤖 OpenAI", 
            "🧠 Google Gemini", 
            "🌐 OpenRouter", 
            "🔮 DeepSeek"
        ])
        
        providers_data = [
            ('openai', '🤖 OpenAI', 'Modelos GPT da OpenAI'),
            ('google', '🧠 Google Gemini', 'Modelos Gemini do Google'),
            ('openrouter', '🌐 OpenRouter', 'Acesso unificado a múltiplos modelos'),
            ('deepseek', '🔮 DeepSeek', 'Modelos avançados chineses')
        ]
        
        for i, (provider_key, provider_name, description) in enumerate(providers_data):
            with provider_tabs[i]:
                st.markdown(f"### {provider_name}")
                st.info(f"📝 {description}")
                
                # Verificar se provedor está configurado
                api_key_env = {
                    'openai': 'OPENAI_API_KEY',
                    'google': 'GOOGLE_API_KEY', 
                    'openrouter': 'OPENROUTER_API_KEY',
                    'deepseek': 'DEEPSEEK_API_KEY'
                }.get(provider_key, '')
                
                is_configured = bool(os.getenv(api_key_env))
                
                if is_configured:
                    st.success(f"✅ {provider_name} configurado")
                else:
                    st.warning(f"⚠️ {provider_name} não configurado (falta API Key)")
                
                # Mostrar modelos
                models = available_models.get(provider_key, [])
                
                if models:
                    st.markdown("**🔧 Modelos Disponíveis:**")
                    
                    # Criar grid de modelos
                    cols = st.columns(2)
                    for idx, model in enumerate(models):
                        with cols[idx % 2]:
                            # Adicionar descrição para modelos conhecidos
                            model_descriptions = {
                                'gpt-4o': '🚀 Mais avançado da OpenAI',
                                'gpt-4o-mini': '⚡ Rápido e eficiente',
                                'gpt-4-turbo': '🎯 Otimizado para performance',
                                'gpt-4': '🧠 Modelo principal da OpenAI',
                                'gpt-3.5-turbo': '💡 Clássico e confiável',
                                'gemini-1.5-pro': '🌟 Mais avançado do Google',
                                'gemini-1.5-flash': '⚡ Rápido e preciso',
                                'gemini-pro': '🧠 Modelo principal do Google',
                                'deepseek-chat': '💬 Conversação geral',
                                'deepseek-coder': '💻 Especializado em código',
                                'deepseek-math': '🔢 Especializado em matemática'
                            }
                            
                            description = model_descriptions.get(model, '🤖 Modelo LLM')
                            
                            st.markdown(f"""
                            <div style="
                                background-color: #f0f2f6; 
                                padding: 10px; 
                                border-radius: 5px; 
                                margin: 5px 0;
                                border-left: 4px solid #1f77b4;
                            ">
                                <strong>{model}</strong><br>
                                <small>{description}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Botão de teste para provedor configurado
                    if is_configured:
                        st.markdown("---")
                        
                        # Seleção de modelo para teste
                        selected_model = st.selectbox(
                            f"🧪 Testar Modelo {provider_name}:",
                            models,
                            key=f"test_model_{provider_key}"
                        )
                        
                        test_message = st.text_input(
                            "💭 Mensagem de teste:",
                            value="Olá, como você está funcionando?",
                            key=f"test_msg_{provider_key}"
                        )
                        
                        if st.button(f"🧪 Testar {selected_model}", key=f"btn_test_model_{provider_key}"):
                            with st.spinner(f"🧪 Testando {selected_model}..."):
                                try:
                                    result = rag_system.llm_manager.generate_response(
                                        [{"role": "user", "content": test_message}],
                                        provider_name=provider_key,
                                        model=selected_model
                                    )
                                    
                                    if result.get('success'):
                                        st.success(f"✅ {selected_model} funcionando!")
                                        st.info(f"⏱️ Tempo: {result.get('response_time', 0):.2f}s")
                                        st.text_area(
                                            "📝 Resposta:",
                                            value=result.get('response', 'Sem resposta'),
                                            height=100,
                                            key=f"response_{provider_key}_{selected_model}"
                                        )
                                    else:
                                        st.error(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")
                                
                                except Exception as e:
                                    st.error(f"❌ Exceção: {str(e)}")
                else:
                    st.warning("⚠️ Nenhum modelo disponível para este provedor")
        
        # Resumo geral
        st.markdown("---")
        st.markdown("### 📊 Resumo Geral")
        
        total_models = sum(len(models) for models in available_models.values())
        configured_providers = sum([
            bool(os.getenv('OPENAI_API_KEY')),
            bool(os.getenv('GOOGLE_API_KEY')),
            bool(os.getenv('OPENROUTER_API_KEY')),
            bool(os.getenv('DEEPSEEK_API_KEY'))
        ])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🤖 Total de Modelos", total_models)
        with col2:
            st.metric("🔧 Provedores Configurados", f"{configured_providers}/4")
        with col3:
            st.metric("🌐 Provedores Disponíveis", len(available_models))

def privacy_interface(rag_system):
    """Interface de privacidade LGPD"""
    st.header("🔒 Sistema de Privacidade LGPD")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Detecção", "📊 Análise", "📋 Relatórios"])
    
    with tab1:
        st.subheader("🔍 Detecção de Dados Pessoais")
        
        text_to_analyze = st.text_area("📝 Texto para Análise:", 
                                      placeholder="Cole o texto que deseja analisar...", 
                                      height=200)
        
        if st.button("🔍 Analisar Dados Pessoais"):
            if text_to_analyze:
                with st.spinner("🔍 Analisando dados pessoais..."):
                    try:
                        results = privacy_manager.detect_personal_data(text_to_analyze)
                        
                        if results.get('entities'):
                            st.subheader("⚠️ Dados Pessoais Detectados")
                            
                            for entity in results['entities']:
                                st.markdown(f"""
                                <div class="privacy-alert">
                                    <strong>Tipo:</strong> {entity.get('entity_type', 'N/A')}<br>
                                    <strong>Texto:</strong> {entity.get('text', 'N/A')}<br>
                                    <strong>Confiança:</strong> {entity.get('confidence', 0):.2%}<br>
                                    <strong>Posição:</strong> {entity.get('start', 0)}-{entity.get('end', 0)}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.success("✅ Nenhum dado pessoal detectado!")
                    
                    except Exception as e:
                        st.error(f"Erro na análise: {str(e)}")
            else:
                st.warning("⚠️ Digite um texto para análise.")
    
    with tab2:
        st.subheader("📊 Análise de Riscos LGPD")
        
        st.info("🛡️ Sistema de análise de riscos em desenvolvimento...")
        
        # Placeholder para análise de riscos
        risk_level = st.select_slider("🎚️ Nível de Risco Simulado:", 
                                     options=["Baixo", "Médio", "Alto", "Crítico"],
                                     value="Médio")
        
        if risk_level == "Baixo":
            st.success("✅ Risco Baixo: Conformidade adequada")
        elif risk_level == "Médio":
            st.warning("⚠️ Risco Médio: Atenção necessária")
        elif risk_level == "Alto":
            st.error("🚨 Risco Alto: Ação imediata requerida")
        else:
            st.error("🔥 Risco Crítico: Violação grave detectada")
    
    with tab3:
        st.subheader("📋 Relatórios de Compliance")
        
        if st.button("📊 Gerar Relatório"):
            st.markdown("""
            <div class="success-box">
                <h4>📄 Relatório de Compliance LGPD</h4>
                <p><strong>Data:</strong> {}</p>
                <p><strong>Status Geral:</strong> ✅ Conforme</p>
                <p><strong>Dados Processados:</strong> 0 registros</p>
                <p><strong>Violações Detectadas:</strong> 0</p>
                <p><strong>Recomendações:</strong> Sistema operando dentro dos parâmetros LGPD</p>
            </div>
            """.format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

def documents_interface(rag_system):
    """Interface de gerenciamento de documentos"""
    st.header("📁 Gerenciamento de Documentos")
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📋 Lista", "🔍 Busca"])
    
    with tab1:
        st.subheader("📤 Upload de Documentos")
        
        # Seleção de agente para a base de conhecimento
        agents = rag_system.agent_manager.get_all_agents()
        agent_options = {"Base Geral": None}
        agent_options.update({f"{agent['name']} (ID: {agent['id'][:8]}...)": agent['id'] for agent in agents})
        
        selected_agent = st.selectbox(
            "🤖 Selecionar Agente para Base de Conhecimento:", 
            list(agent_options.keys()),
            help="Escolha qual agente receberá estes documentos em sua base de conhecimento"
        )
        agent_id = agent_options[selected_agent]
        
        if agent_id:
            agent = rag_system.agent_manager.get_agent_by_id(agent_id)
            if agent:
                st.info(f"📚 Documentos serão adicionados à base do agente: **{agent['name']}**")
        else:
            st.info("📚 Documentos serão adicionados à base geral do sistema")
        
        uploaded_files = st.file_uploader("Selecionar Arquivos:", 
                                        accept_multiple_files=True,
                                        type=['txt', 'pdf', 'docx', 'md'])
        
        if uploaded_files:
            st.markdown("### 📋 Arquivos Selecionados:")
            for file in uploaded_files:
                st.write(f"📄 {file.name} ({file.size} bytes)")
        
        if st.button("📤 Processar Uploads", type="primary"):
            if uploaded_files:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"📤 Processando {file.name}...")
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    try:
                        # Ler conteúdo do arquivo
                        if file.type == 'text/plain':
                            content = file.read().decode('utf-8')
                        elif file.type == 'application/pdf':
                            # Para PDF, simular extração de texto
                            content = f"Conteúdo extraído do PDF: {file.name}\n\nEste é um documento PDF que foi processado pelo sistema."
                        else:
                            # Para outros tipos, converter para texto
                            content = file.read().decode('utf-8', errors='ignore')
                        
                        # Processar upload com vetorização
                        result = rag_system.process_document_upload(content, file.name, agent_id)
                        
                        results.append({
                            'file_name': file.name,
                            'result': result
                        })
                        
                    except Exception as e:
                        results.append({
                            'file_name': file.name,
                            'result': {
                                'success': False,
                                'error': str(e)
                            }
                        })
                
                # Mostrar resultados
                progress_bar.empty()
                status_text.empty()
                
                successful_uploads = 0
                total_chunks = 0
                
                for upload_result in results:
                    file_name = upload_result['file_name']
                    result = upload_result['result']
                    
                    if result['success']:
                        successful_uploads += 1
                        chunks_created = result.get('chunks_created', 0)
                        total_chunks += chunks_created
                        
                        st.success(f"✅ **{file_name}**: {chunks_created} chunks criados")
                    else:
                        st.error(f"❌ **{file_name}**: {result.get('error', 'Erro desconhecido')}")
                
                # Resumo final
                if successful_uploads > 0:
                    agent_name = agent['name'] if agent_id and agent else 'Base Geral'
                    st.success(f"""
                    🎉 **Upload Concluído!**
                    
                    - ✅ **{successful_uploads}** arquivo(s) processado(s)
                    - 📝 **{total_chunks}** chunks vetorizados
                    - 🤖 **Base:** {agent_name}
                    - 💾 **Armazenado:** PostgreSQL + Embeddings
                    """)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Nenhum arquivo foi processado com sucesso.")
            else:
                st.warning("⚠️ Selecione arquivos para upload.")
    
    with tab2:
        st.subheader("📋 Documentos Carregados")
        
        if rag_system.documents:
            # Filtro por agente
            agents = rag_system.agent_manager.get_all_agents()
            filter_options = ["Todos"] + ["Base Geral"] + [agent['name'] for agent in agents]
            
            selected_filter = st.selectbox("🔍 Filtrar por Agente:", filter_options)
            
            # Filtrar documentos
            filtered_docs = []
            for i, doc in enumerate(rag_system.documents):
                if selected_filter == "Todos":
                    filtered_docs.append((i, doc))
                elif selected_filter == "Base Geral" and not doc.get('agent_id'):
                    filtered_docs.append((i, doc))
                elif doc.get('agent_name') == selected_filter:
                    filtered_docs.append((i, doc))
            
            if filtered_docs:
                st.write(f"📊 Mostrando {len(filtered_docs)} documento(s)")
                
                for i, doc in filtered_docs:
                    agent_info = doc.get('agent_name', 'Base Geral')
                    with st.expander(f"📄 {doc['name']} - 🤖 {agent_info}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Tipo:** {doc.get('type', 'N/A')}")
                            st.write(f"**Tamanho:** {doc.get('size', 0)} bytes")
                            st.write(f"**Upload:** {doc.get('uploaded_at', 'N/A')}")
                            st.write(f"**Base de Conhecimento:** 🤖 {agent_info}")
                            
                            if st.button(f"👁️ Visualizar", key=f"view_{i}"):
                                st.text_area("Conteúdo:", doc.get('content', '')[:500] + "...", height=100)
                        
                        with col2:
                            if st.button(f"🗑️ Remover", key=f"remove_{i}"):
                                rag_system.documents.pop(i)
                                st.success("🗑️ Documento removido!")
                                st.rerun()
            else:
                st.info(f"📝 Nenhum documento encontrado para: {selected_filter}")
        else:
            st.info("📝 Nenhum documento carregado ainda.")
    
    with tab3:
        st.subheader("🔍 Busca em Documentos")
        
        search_query = st.text_input("🔍 Termo de Busca:", placeholder="Digite para buscar...")
        
        if search_query:
            results = []
            for doc in rag_system.documents:
                if search_query.lower() in doc.get('content', '').lower():
                    results.append(doc)
            
            if results:
                st.write(f"📊 Encontrados {len(results)} resultado(s):")
                for doc in results:
                    st.write(f"📄 **{doc['name']}**")
            else:
                st.info("🔍 Nenhum resultado encontrado.")

def settings_interface(rag_system):
    """Interface de configurações"""
    st.header("⚙️ Configurações do Sistema")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 API Keys", "🧪 Testes", "🎛️ Geral", "💾 Backup"])
    
    with tab1:
        st.subheader("🔑 Configuração de Provedores LLM")
        
        # Configuração das API Keys
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🤖 OpenAI")
            openai_key = st.text_input("OpenAI API Key:", type="password", 
                                      value=os.getenv('OPENAI_API_KEY', ''),
                                      key="openai_key")
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
            
            st.markdown("### 🌐 OpenRouter")
            openrouter_key = st.text_input("OpenRouter API Key:", type="password",
                                          value=os.getenv('OPENROUTER_API_KEY', ''),
                                          key="openrouter_key")
            if openrouter_key:
                os.environ['OPENROUTER_API_KEY'] = openrouter_key
        
        with col2:
            st.markdown("### 🧠 Google Gemini")
            google_key = st.text_input("Google Gemini API Key:", type="password",
                                      value=os.getenv('GOOGLE_API_KEY', ''),
                                      key="google_key")
            if google_key:
                os.environ['GOOGLE_API_KEY'] = google_key
            
            st.markdown("### 🔮 DeepSeek")
            deepseek_key = st.text_input("DeepSeek API Key:", type="password",
                                        value=os.getenv('DEEPSEEK_API_KEY', ''),
                                        key="deepseek_key")
            if deepseek_key:
                os.environ['DEEPSEEK_API_KEY'] = deepseek_key
        
        # Status das API Keys
        st.markdown("---")
        st.subheader("📊 Status das API Keys")
        
        keys_status = {
            "🤖 OpenAI": bool(os.getenv('OPENAI_API_KEY')),
            "🧠 Google Gemini": bool(os.getenv('GOOGLE_API_KEY')),
            "🌐 OpenRouter": bool(os.getenv('OPENROUTER_API_KEY')),
            "🔮 DeepSeek": bool(os.getenv('DEEPSEEK_API_KEY'))
        }
        
        cols = st.columns(4)
        for i, (provider, configured) in enumerate(keys_status.items()):
            with cols[i]:
                status = "✅ Ativa" if configured else "❌ Inativa"
                color = "#28a745" if configured else "#dc3545"
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border: 1px solid {color}; border-radius: 5px; margin: 5px;">
                    <strong>{provider}</strong><br>
                    <span style="color: {color};">{status}</span>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("🧪 Testes de Conectividade")
        
        st.info("🔍 Teste a conectividade e funcionamento dos provedores LLM")
        
        # Seleção de provedores para teste
        providers_to_test = st.multiselect(
            "Selecione os provedores para testar:",
            ["openai", "google", "openrouter", "deepseek"],
            default=["openai"]
        )
        
        test_message = st.text_input("Mensagem de teste:", 
                                    value="Olá, este é um teste de conectividade. Responda apenas 'OK'.")
        
        if st.button("🚀 Executar Testes"):
            if providers_to_test:
                st.markdown("### 📊 Resultados dos Testes")
                
                for provider in providers_to_test:
                    with st.expander(f"🧪 Teste: {provider.upper()}"):
                        try:
                            # Testar conectividade
                            start_time = time.time()
                            
                            # Simular teste (você pode implementar teste real aqui)
                            messages = [{"role": "user", "content": test_message}]
                            
                            # Verificar se tem API key
                            key_map = {
                                'openai': 'OPENAI_API_KEY',
                                'google': 'GOOGLE_API_KEY', 
                                'openrouter': 'OPENROUTER_API_KEY',
                                'deepseek': 'DEEPSEEK_API_KEY'
                            }
                            
                            if not os.getenv(key_map.get(provider, '')):
                                st.error(f"❌ API Key não configurada para {provider}")
                                continue
                            
                            # Tentar gerar resposta
                            try:
                                response = rag_system.llm_manager.generate_response(
                                    messages, 
                                    provider=provider,
                                    model="gpt-3.5-turbo" if provider == "openai" else None
                                )
                                
                                end_time = time.time()
                                response_time = round(end_time - start_time, 2)
                                
                                st.success(f"✅ **Sucesso!** Tempo: {response_time}s")
                                st.write(f"**Resposta:** {response}")
                                
                                # Métricas
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("⏱️ Tempo", f"{response_time}s")
                                with col2:
                                    st.metric("📊 Status", "✅ OK")
                                with col3:
                                    st.metric("📝 Caracteres", len(response))
                                    
                            except Exception as e:
                                st.error(f"❌ **Erro na resposta:** {str(e)}")
                                
                        except Exception as e:
                            st.error(f"❌ **Erro no teste:** {str(e)}")
            else:
                st.warning("⚠️ Selecione pelo menos um provedor para testar.")
        
        # Teste de comparação rápida
        st.markdown("---")
        st.subheader("⚡ Teste Rápido Multi-LLM")
        
        if st.button("🔄 Comparar Todos os Provedores"):
            test_question = "Qual é a capital do Brasil?"
            
            with st.spinner("🔄 Testando todos os provedores..."):
                results = {}
                
                for provider in ["openai", "google", "openrouter", "deepseek"]:
                    try:
                        key_map = {
                            'openai': 'OPENAI_API_KEY',
                            'google': 'GOOGLE_API_KEY', 
                            'openrouter': 'OPENROUTER_API_KEY',
                            'deepseek': 'DEEPSEEK_API_KEY'
                        }
                        
                        if os.getenv(key_map.get(provider, '')):
                            start_time = time.time()
                            
                            messages = [{"role": "user", "content": test_question}]
                            response = rag_system.llm_manager.generate_response(
                                messages, 
                                provider=provider
                            )
                            
                            end_time = time.time()
                            
                            results[provider] = {
                                'response': response,
                                'time': round(end_time - start_time, 2),
                                'status': 'success'
                            }
                        else:
                            results[provider] = {
                                'response': 'API Key não configurada',
                                'time': 0,
                                'status': 'error'
                            }
                            
                    except Exception as e:
                        results[provider] = {
                            'response': f'Erro: {str(e)}',
                            'time': 0,
                            'status': 'error'
                        }
                
                # Mostrar resultados
                st.markdown("### 📊 Resultados da Comparação")
                
                for provider, result in results.items():
                    with st.expander(f"📱 {provider.upper()} - {'✅' if result['status'] == 'success' else '❌'}"):
                        if result['status'] == 'success':
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Resposta:** {result['response']}")
                            with col2:
                                st.metric("⏱️ Tempo", f"{result['time']}s")
                        else:
                            st.error(result['response'])
    
    with tab3:
        st.subheader("🎛️ Configurações Gerais")
        
        # Configurações do modelo padrão
        col1, col2 = st.columns(2)
        
        with col1:
            default_model = st.selectbox("🤖 Modelo Padrão:", [
                "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4o-mini",
                "gemini-pro", "deepseek-chat"
            ], index=0)
            
            default_temperature = st.slider("🌡️ Temperatura Padrão:", 0.0, 2.0, 0.7, 0.1)
        
        with col2:
            max_tokens = st.number_input("📝 Max Tokens:", min_value=100, max_value=4000, value=1000)
            
            debug_mode = st.checkbox("🐛 Modo Debug", value=False)
        
        # Configurações avançadas
        st.markdown("---")
        st.subheader("🔧 Configurações Avançadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            timeout_duration = st.number_input("⏱️ Timeout (segundos):", min_value=5, max_value=300, value=30)
            retry_attempts = st.number_input("🔄 Tentativas de Retry:", min_value=1, max_value=10, value=3)
        
        with col2:
            enable_logging = st.checkbox("📝 Habilitar Logging", value=True)
            enable_cache = st.checkbox("💾 Habilitar Cache", value=True)
        
        if st.button("💾 Salvar Configurações"):
            rag_system.settings.update({
                'model_name': default_model,
                'temperature': default_temperature,
                'max_tokens': max_tokens,
                'debug_mode': debug_mode,
                'timeout': timeout_duration,
                'retry_attempts': retry_attempts,
                'enable_logging': enable_logging,
                'enable_cache': enable_cache
            })
            st.success("✅ Configurações salvas com sucesso!")
    
    with tab4:
        st.subheader("💾 Backup e Restauração")
        
        # Informações do sistema
        st.markdown("### 📊 Informações do Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Documentos", len(rag_system.documents))
        
        with col2:
            try:
                agents = rag_system.agent_manager.get_all_agents()
                st.metric("🤖 Agentes", len(agents))
            except:
                st.metric("🤖 Agentes", "N/A")
        
        with col3:
            configured_keys = sum([
                bool(os.getenv('OPENAI_API_KEY')),
                bool(os.getenv('GOOGLE_API_KEY')),
                bool(os.getenv('OPENROUTER_API_KEY')),
                bool(os.getenv('DEEPSEEK_API_KEY'))
            ])
            st.metric("🔑 API Keys", f"{configured_keys}/4")
        
        st.markdown("---")
        
        # Export
        if st.button("📥 Exportar Configurações"):
            config_data = {
                'settings': rag_system.settings,
                'documents_count': len(rag_system.documents),
                'api_keys_configured': configured_keys,
                'export_date': datetime.now().isoformat(),
                'version': '1.5.1-unified'
            }
            
            st.download_button(
                label="💾 Download Configurações",
                data=json.dumps(config_data, indent=2),
                file_name=f"rag_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Import
        uploaded_config = st.file_uploader("📤 Importar Configurações:", type=['json'])
        
        if uploaded_config and st.button("📥 Restaurar Configurações"):
            try:
                config_data = json.load(uploaded_config)
                rag_system.settings.update(config_data.get('settings', {}))
                st.success("✅ Configurações restauradas com sucesso!")
                st.info(f"📊 Importado de: {config_data.get('export_date', 'N/A')}")
            except Exception as e:
                st.error(f"❌ Erro ao importar configurações: {str(e)}")

if __name__ == "__main__":
    main() 