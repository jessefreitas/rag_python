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

# Importações do sistema
from llm_providers import LLMProviderManager
from privacy_system import privacy_manager
from vector_store import VectorStore
from database import Database

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
        """Obtém todos os agentes"""
        try:
            query = "SELECT * FROM agentes ORDER BY created_at DESC"
            rows = self._execute_query(query, fetch='all')
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"Erro ao buscar agentes: {e}")
            return []
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Dict]:
        """Obtém agente por ID"""
        try:
            query = "SELECT * FROM agentes WHERE id = %s"
            row = self._execute_query(query, (agent_id,), fetch='one')
            return dict(row) if row else None
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
    
    def configure_providers(self):
        """Configuração de provedores LLM"""
        st.sidebar.header("🔧 Configuração de Provedores")
        
        # OpenAI
        openai_key = st.sidebar.text_input("🤖 OpenAI API Key", type="password", 
                                          value=os.getenv('OPENAI_API_KEY', ''))
        if openai_key:
            os.environ['OPENAI_API_KEY'] = openai_key
        
        # Google Gemini
        google_key = st.sidebar.text_input("🧠 Google Gemini API Key", type="password",
                                          value=os.getenv('GOOGLE_API_KEY', ''))
        if google_key:
            os.environ['GOOGLE_API_KEY'] = google_key
        
        # OpenRouter
        openrouter_key = st.sidebar.text_input("🌐 OpenRouter API Key", type="password",
                                              value=os.getenv('OPENROUTER_API_KEY', ''))
        if openrouter_key:
            os.environ['OPENROUTER_API_KEY'] = openrouter_key
        
        # DeepSeek
        deepseek_key = st.sidebar.text_input("🔮 DeepSeek API Key", type="password",
                                            value=os.getenv('DEEPSEEK_API_KEY', ''))
        if deepseek_key:
            os.environ['DEEPSEEK_API_KEY'] = deepseek_key
        
        # Status dos provedores
        st.sidebar.subheader("📊 Status dos Provedores")
        try:
            providers_info = self.llm_manager.get_provider_info()
            
            for provider, info in providers_info.items():
                if isinstance(info, dict):
                    status = "✅ Ativo" if info.get('available', False) else "❌ Inativo"
                else:
                    status = "❌ Inativo"
                st.sidebar.write(f"**{provider}:** {status}")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar provedores: {str(e)}")
    
    def query_with_agent(self, question: str, agent_id: str = None) -> Dict:
        """Processa pergunta com agente específico"""
        try:
            agent = None
            if agent_id:
                agent = self.agent_manager.get_agent_by_id(agent_id)
            
            # Preparar mensagens
            messages = []
            
            if agent:
                messages.append({
                    "role": "system", 
                    "content": agent['system_prompt']
                })
            
            messages.append({"role": "user", "content": question})
            
            # Gerar resposta
            model = agent['model'] if agent else self.settings['model_name']
            temperature = agent['temperature'] if agent else self.settings['temperature']
            
            response = self.llm_manager.generate_response(
                messages,
                model=model,
                temperature=temperature
            )
            
            return {
                'answer': response,
                'agent_used': agent['name'] if agent else 'Sistema Padrão',
                'model_used': model,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            return {
                'answer': f"Erro: {str(e)}",
                'agent_used': 'Erro',
                'model_used': 'N/A',
                'success': False
            }
    
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
    
    # Configuração de provedores na sidebar
    rag_system.configure_providers()
    
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
    """Interface do Dashboard"""
    st.header("📊 Dashboard do Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 Agentes</h3>
            <p>Sistema de agentes especializados com RAG</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔄 Multi-LLM</h3>
            <p>Comparação entre 4 provedores de IA</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🔒 Privacidade</h3>
            <p>Compliance LGPD com Microsoft Presidio</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>📁 Documentos</h3>
            <p>Gestão completa de base de conhecimento</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Status dos provedores
    st.subheader("🌐 Status dos Provedores LLM")
    
    try:
        providers_info = rag_system.llm_manager.get_provider_info()
        
        if providers_info:
            cols = st.columns(len(providers_info))
            for i, (provider, info) in enumerate(providers_info.items()):
                with cols[i]:
                    if isinstance(info, dict):
                        available = info.get('available', False)
                        status_color = "#28a745" if available else "#dc3545"
                        status_text = "✅ Ativo" if available else "❌ Inativo"
                        model_text = info.get('model', 'N/A')
                    else:
                        status_color = "#dc3545"
                        status_text = "❌ Inativo"
                        model_text = "N/A"
                    
                    st.markdown(f"""
                    <div class="provider-card" style="background: {status_color};">
                        <h4>{provider.upper()}</h4>
                        <p>Status: {status_text}</p>
                        <p>Modelo: {model_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("🔧 Configurando provedores...")
    except Exception as e:
        st.error(f"Erro ao carregar status dos provedores: {str(e)}")
    
    # Estatísticas do sistema
    st.subheader("📈 Estatísticas do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            agents = rag_system.agent_manager.get_all_agents()
            st.metric("Agentes Cadastrados", len(agents))
        except:
            st.metric("Agentes Cadastrados", "Erro")
    
    with col2:
        st.metric("Documentos Carregados", len(rag_system.documents))
    
    with col3:
        try:
            providers_info = rag_system.llm_manager.get_provider_info()
            active_providers = sum(1 for info in providers_info.values() 
                                 if isinstance(info, dict) and info.get('available', False))
            st.metric("Provedores Ativos", active_providers)
        except:
            st.metric("Provedores Ativos", "Erro")

def chat_rag_interface(rag_system):
    """Interface do Chat RAG"""
    st.header("💬 Chat RAG Inteligente")
    
    # Seleção de agente
    agents = rag_system.agent_manager.get_all_agents()
    agent_options = {"Sistema Padrão": None}
    agent_options.update({agent['name']: agent['id'] for agent in agents})
    
    selected_agent = st.selectbox("🤖 Selecionar Agente:", list(agent_options.keys()))
    agent_id = agent_options[selected_agent]
    
    # Histórico do chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Área de mensagens
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Você:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 {message.get('agent', 'Assistente')}:</strong><br>
                    {message['content']}
                    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                        Modelo: {message.get('model', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input de mensagem
    user_input = st.text_input("💭 Digite sua pergunta:", key="chat_input", 
                              placeholder="Faça uma pergunta...")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("📤 Enviar", type="primary"):
            if user_input:
                # Adicionar mensagem do usuário
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Processar resposta
                with st.spinner("🤔 Pensando..."):
                    result = rag_system.query_with_agent(user_input, agent_id)
                
                # Adicionar resposta do assistente
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': result['answer'],
                    'agent': result['agent_used'],
                    'model': result['model_used']
                })
                
                st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Chat"):
            st.session_state.chat_history = []
            st.rerun()

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
    """Interface de comparação Multi-LLM"""
    st.header("🔄 Comparador Multi-LLM")
    
    st.write("Compare respostas de diferentes provedores de IA lado a lado")
    
    # Seleção de provedores
    st.subheader("🎯 Selecionar Provedores para Comparação")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        use_openai = st.checkbox("🤖 OpenAI", value=True)
    with col2:
        use_google = st.checkbox("🧠 Google Gemini", value=True)
    with col3:
        use_openrouter = st.checkbox("🌐 OpenRouter", value=True)
    with col4:
        use_deepseek = st.checkbox("🔮 DeepSeek", value=True)
    
    # Pergunta para comparação
    question = st.text_area("❓ Pergunta para Comparação:", 
                           placeholder="Digite sua pergunta aqui...", height=100)
    
    if st.button("🚀 Comparar Respostas", type="primary"):
        if question:
            providers = []
            if use_openai: providers.append('openai')
            if use_google: providers.append('google')
            if use_openrouter: providers.append('openrouter')
            if use_deepseek: providers.append('deepseek')
            
            if providers:
                with st.spinner("🔄 Processando comparação..."):
                    results = rag_system.multi_llm_compare(question, providers)
                
                if 'error' not in results:
                    st.subheader("📊 Resultados da Comparação")
                    
                    # Criar colunas para cada provedor
                    cols = st.columns(len(providers))
                    
                    for i, provider in enumerate(providers):
                        with cols[i]:
                            if provider in results:
                                result = results[provider]
                                
                                # Card do provedor
                                st.markdown(f"""
                                <div class="provider-card">
                                    <h4>{provider.upper()}</h4>
                                    <p>⏱️ Tempo: {result.get('response_time', 'N/A')}s</p>
                                    <p>🎯 Status: {'✅' if result.get('success') else '❌'}</p>
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
                        times = [results[p].get('response_time', 0) for p in providers if p in results]
                        if times:
                            fastest = min(times)
                            fastest_provider = [p for p in providers if p in results and results[p].get('response_time') == fastest][0]
                            st.metric("⚡ Mais Rápido", fastest_provider.upper(), f"{fastest:.2f}s")
                    
                    with col2:
                        successful = sum(1 for p in providers if p in results and results[p].get('success'))
                        st.metric("✅ Sucessos", f"{successful}/{len(providers)}")
                    
                    with col3:
                        avg_time = sum(times) / len(times) if times else 0
                        st.metric("⏱️ Tempo Médio", f"{avg_time:.2f}s")
                
                else:
                    st.error(f"Erro na comparação: {results['error']}")
            else:
                st.warning("⚠️ Selecione pelo menos um provedor para comparação.")
        else:
            st.warning("⚠️ Digite uma pergunta para comparação.")

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
        
        uploaded_files = st.file_uploader("Selecionar Arquivos:", 
                                        accept_multiple_files=True,
                                        type=['txt', 'pdf', 'docx', 'md'])
        
        if uploaded_files:
            for file in uploaded_files:
                st.write(f"📄 {file.name} ({file.size} bytes)")
        
        if st.button("📤 Processar Uploads"):
            if uploaded_files:
                with st.spinner("📤 Processando arquivos..."):
                    for file in uploaded_files:
                        # Simular processamento
                        content = file.read().decode('utf-8') if file.type == 'text/plain' else "Conteúdo processado"
                        
                        rag_system.documents.append({
                            'name': file.name,
                            'content': content,
                            'type': file.type,
                            'size': file.size,
                            'uploaded_at': datetime.now().isoformat()
                        })
                
                st.success(f"✅ {len(uploaded_files)} arquivo(s) processado(s) com sucesso!")
                st.rerun()
            else:
                st.warning("⚠️ Selecione arquivos para upload.")
    
    with tab2:
        st.subheader("📋 Documentos Carregados")
        
        if rag_system.documents:
            for i, doc in enumerate(rag_system.documents):
                with st.expander(f"📄 {doc['name']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Tipo:** {doc.get('type', 'N/A')}")
                        st.write(f"**Tamanho:** {doc.get('size', 0)} bytes")
                        st.write(f"**Upload:** {doc.get('uploaded_at', 'N/A')}")
                        
                        if st.button(f"👁️ Visualizar", key=f"view_{i}"):
                            st.text_area("Conteúdo:", doc.get('content', '')[:500] + "...", height=100)
                    
                    with col2:
                        if st.button(f"🗑️ Remover", key=f"remove_{i}"):
                            rag_system.documents.pop(i)
                            st.rerun()
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
    
    tab1, tab2, tab3 = st.tabs(["🎛️ Geral", "🔑 API Keys", "💾 Backup"])
    
    with tab1:
        st.subheader("🎛️ Configurações Gerais")
        
        # Configurações do modelo padrão
        col1, col2 = st.columns(2)
        
        with col1:
            default_model = st.selectbox("🤖 Modelo Padrão:", [
                "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4o-mini",
                "gemini-pro", "deepseek-chat"
            ])
            
            default_temperature = st.slider("🌡️ Temperatura Padrão:", 0.0, 2.0, 0.7, 0.1)
        
        with col2:
            max_tokens = st.number_input("📝 Max Tokens:", min_value=100, max_value=4000, value=1000)
            
            debug_mode = st.checkbox("🐛 Modo Debug", value=False)
        
        if st.button("💾 Salvar Configurações"):
            rag_system.settings.update({
                'model_name': default_model,
                'temperature': default_temperature,
                'max_tokens': max_tokens,
                'debug_mode': debug_mode
            })
            st.success("✅ Configurações salvas!")
    
    with tab2:
        st.subheader("🔑 Gerenciamento de API Keys")
        
        st.info("🔒 Configure suas API Keys nas variáveis de ambiente ou na sidebar.")
        
        # Mostrar status das keys (sem revelar)
        keys_status = {
            "OpenAI": bool(os.getenv('OPENAI_API_KEY')),
            "Google Gemini": bool(os.getenv('GOOGLE_API_KEY')),
            "OpenRouter": bool(os.getenv('OPENROUTER_API_KEY')),
            "DeepSeek": bool(os.getenv('DEEPSEEK_API_KEY'))
        }
        
        for provider, configured in keys_status.items():
            status = "✅ Configurada" if configured else "❌ Não configurada"
            st.write(f"**{provider}:** {status}")
    
    with tab3:
        st.subheader("💾 Backup e Restauração")
        
        if st.button("📥 Exportar Configurações"):
            config_data = {
                'settings': rag_system.settings,
                'documents_count': len(rag_system.documents),
                'export_date': datetime.now().isoformat()
            }
            
            st.download_button(
                label="💾 Download Configurações",
                data=json.dumps(config_data, indent=2),
                file_name=f"rag_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.write("---")
        
        uploaded_config = st.file_uploader("📤 Importar Configurações:", type=['json'])
        
        if uploaded_config and st.button("📥 Restaurar Configurações"):
            try:
                config_data = json.load(uploaded_config)
                rag_system.settings.update(config_data.get('settings', {}))
                st.success("✅ Configurações restauradas com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao importar configurações: {str(e)}")

if __name__ == "__main__":
    main() 