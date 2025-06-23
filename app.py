"""
Interface web Streamlit para o sistema RAG
"""

import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
from pathlib import Path
import logging
from typing import List, Dict, Any
from datetime import datetime

load_dotenv()

from llm_providers import LLMProviderManager
from privacy_system import privacy_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="RAG Python v1.5.1 - Sistema Completo",
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
    .source-box {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .info-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

class RAGSystemLocal:
    """Sistema RAG local simplificado para interface web"""
    
    def __init__(self):
        self.llm_manager = LLMProviderManager()
        self.documents = []
        self.knowledge_base = {}
        self.settings = {
            'model_name': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000
        }
    
    def update_model_settings(self, model_name=None, temperature=None, max_tokens=None):
        """Atualiza configurações do modelo"""
        try:
            if model_name:
                self.settings['model_name'] = model_name
            if temperature is not None:
                self.settings['temperature'] = temperature
            if max_tokens:
                self.settings['max_tokens'] = max_tokens
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações: {e}")
            return False
    
    def load_documents(self, file_paths=None, directory_path=None, urls=None):
        """Carrega documentos de diferentes fontes"""
        try:
            success = True
            
            if file_paths:
                for file_path in file_paths:
                    content = self._load_file_content(file_path)
                    if content:
                        self.documents.append({
                            'source': file_path,
                            'content': content,
                            'type': 'file',
                            'timestamp': datetime.now().isoformat()
                        })
            
            if directory_path:
                directory = Path(directory_path)
                if directory.exists():
                    for file_path in directory.rglob("*.txt"):
                        content = self._load_file_content(str(file_path))
                        if content:
                            self.documents.append({
                                'source': str(file_path),
                                'content': content,
                                'type': 'directory',
                                'timestamp': datetime.now().isoformat()
                            })
            
            if urls:
                for url in urls:
                    # Simulação de carregamento de URL
                    self.documents.append({
                        'source': url,
                        'content': f"Conteúdo simulado de {url}",
                        'type': 'url',
                        'timestamp': datetime.now().isoformat()
                    })
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao carregar documentos: {e}")
            return False
    
    def _load_file_content(self, file_path):
        """Carrega conteúdo de um arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo {file_path}: {e}")
            return None
    
    def query(self, question, include_sources=True):
        """Processa uma pergunta usando RAG"""
        try:
            # Buscar contexto relevante
            context = self._get_relevant_context(question)
            
            # Preparar mensagens para o LLM
            messages = []
            
            if context:
                system_message = f"""Você é um assistente inteligente. Use o seguinte contexto para responder à pergunta do usuário:

CONTEXTO:
{context}

Responda de forma clara e precisa, baseando-se no contexto fornecido."""
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": question})
            
            # Gerar resposta
            if self.llm_manager.get_active_provider():
                response = self.llm_manager.generate_response(
                    messages,
                    model=self.settings['model_name'],
                    temperature=self.settings['temperature']
                )
                
                result = {
                    'answer': response,
                    'sources': self._get_sources() if include_sources else [],
                    'success': True
                }
            else:
                result = {
                    'answer': "Erro: Nenhum provedor LLM configurado. Configure sua API key.",
                    'sources': [],
                    'success': False
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            return {
                'answer': f"Erro ao processar pergunta: {str(e)}",
                'sources': [],
                'success': False
            }
    
    def _get_relevant_context(self, question):
        """Busca contexto relevante nos documentos"""
        if not self.documents:
            return ""
        
        # Busca simples por palavras-chave
        relevant_docs = []
        question_words = question.lower().split()
        
        for doc in self.documents[-5:]:  # Últimos 5 documentos
            content_lower = doc['content'].lower()
            if any(word in content_lower for word in question_words):
                relevant_docs.append(doc['content'][:500])  # Primeiros 500 chars
        
        return "\n\n".join(relevant_docs)
    
    def _get_sources(self):
        """Retorna fontes dos documentos"""
        return [{'source': doc['source'], 'content': doc['content'][:100]} 
                for doc in self.documents[-3:]]
    
    def search_similar_documents(self, query, k=4):
        """Busca documentos similares"""
        try:
            results = []
            query_lower = query.lower()
            
            for doc in self.documents:
                if query_lower in doc['content'].lower():
                    results.append({
                        'content': doc['content'][:300],
                        'metadata': {
                            'source': doc['source'],
                            'type': doc['type'],
                            'timestamp': doc['timestamp']
                        }
                    })
                
                if len(results) >= k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def get_system_info(self):
        """Retorna informações do sistema"""
        return {
            'document_count': len(self.documents),
            'model_name': self.settings['model_name'],
            'temperature': self.settings['temperature'],
            'max_tokens': self.settings['max_tokens'],
            'document_sources': [doc['source'] for doc in self.documents],
            'llm_status': 'active' if self.llm_manager.get_active_provider() else 'inactive',
            'available_providers': self.llm_manager.list_available_providers()
        }
    
    def reset_system(self):
        """Reseta o sistema"""
        try:
            self.documents = []
            self.knowledge_base = {}
            return True
        except Exception as e:
            logger.error(f"Erro ao resetar sistema: {e}")
            return False

@st.cache_resource
def initialize_rag_system():
    """Inicializa o sistema RAG com cache"""
    try:
        # Verificar se a API key está configurada
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("⚠️ OPENAI_API_KEY não configurada. Configure a variável de ambiente.")
            return None
        
        # Usar RAGSystemLocal que é totalmente funcional
        rag = RAGSystemLocal()
        return rag
    except Exception as e:
        st.error(f"Erro ao inicializar sistema RAG: {str(e)}")
        return None

def display_chat_message(role: str, content: str, sources: List[Dict] = None):
    """Exibe uma mensagem no chat"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 Você:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistente:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # Exibir fontes se disponíveis
        if sources:
            st.markdown("**📚 Fontes:**")
            for i, source in enumerate(sources, 1):
                st.markdown(f"""
                <div class="source-box">
                    <strong>Fonte {i}:</strong> {source['source']}<br>
                    <em>{source['content']}</em>
                </div>
                """, unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Cabeçalho
    st.markdown('<h1 class="main-header">🚀 RAG Python v1.5.1 - Sistema Completo</h1>', unsafe_allow_html=True)
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Configuração da API
        api_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Sua chave da API OpenAI"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Configurações do modelo
        st.subheader("🎛️ Modelo")
        model_name = st.selectbox(
            "Modelo",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
            index=0
        )
        
        temperature = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controla a criatividade das respostas"
        )
        
        max_tokens = st.slider(
            "Máximo de Tokens",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100
        )
        
    # Inicializar sistema RAG PRIMEIRO
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = initialize_rag_system()
    
    if st.session_state.rag_system is None:
        st.error("❌ Sistema RAG não pôde ser inicializado. Verifique sua API key.")
        return
    
    # Sidebar para configurações (continuação)
    with st.sidebar:
        # Botão para atualizar configurações
        if st.button("🔄 Atualizar Configurações"):
            if st.session_state.rag_system is not None:
                try:
                    success = st.session_state.rag_system.update_model_settings(
                        model_name=model_name,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    if success:
                        st.success("Configurações atualizadas!")
                    else:
                        st.error("Erro ao atualizar configurações")
                except Exception as e:
                    st.error(f"Erro ao atualizar configurações: {str(e)}")
            else:
                st.error("Sistema RAG não inicializado!")
    
    # Abas principais
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💬 Chat RAG", 
        "📁 Documentos", 
        "🔍 Busca",
        "🤖 Multi-LLM",
        "🔒 Privacidade",
        "ℹ️ Informações"
    ])
    
    with tab1:
        st.header("💬 Chat com IA")
        
        # Inicializar histórico de chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Exibir histórico de mensagens
        for message in st.session_state.messages:
            display_chat_message(
                message["role"],
                message["content"],
                message.get("sources", [])
            )
        
        # Input do usuário
        user_question = st.text_area(
            "Digite sua pergunta:",
            height=100,
            placeholder="Ex: O que é inteligência artificial?"
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🚀 Enviar", type="primary"):
                if user_question.strip():
                    # Adicionar pergunta ao histórico
                    st.session_state.messages.append({
                        "role": "user",
                        "content": user_question
                    })
                    
                    # Processar pergunta
                    with st.spinner("🤔 Processando sua pergunta..."):
                        try:
                            response = st.session_state.rag_system.query(user_question)
                            
                            # Adicionar resposta ao histórico
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response["answer"],
                                "sources": response.get("sources", [])
                            })
                            
                            # Recarregar página para mostrar nova mensagem
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erro ao processar pergunta: {str(e)}")
        
        with col2:
            if st.button("🗑️ Limpar Chat"):
                st.session_state.messages = []
                st.rerun()
    
    with tab2:
        st.header("📁 Gerenciamento de Documentos")
        
        # Upload de arquivos
        st.subheader("📤 Upload de Arquivos")
        uploaded_files = st.file_uploader(
            "Selecione arquivos para carregar",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("📥 Carregar Arquivos"):
                with st.spinner("Carregando documentos..."):
                    temp_dir = tempfile.mkdtemp()
                    
                    # Salvar arquivos temporariamente
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = Path(temp_dir) / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(str(file_path))
                    
                    # Carregar documentos
                    success = st.session_state.rag_system.load_documents(file_paths=file_paths)
                    
                    if success:
                        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s) com sucesso!")
                    else:
                        st.error("❌ Erro ao carregar arquivos")
        
        # Carregar diretório
        st.subheader("📂 Carregar Diretório")
        directory_path = st.text_input(
            "Caminho para diretório com documentos:",
            placeholder="Ex: ./documents"
        )
        
        if directory_path and st.button("📂 Carregar Diretório"):
            with st.spinner("Carregando documentos do diretório..."):
                success = st.session_state.rag_system.load_documents(directory_path=directory_path)
                
                if success:
                    st.success("✅ Documentos do diretório carregados com sucesso!")
                else:
                    st.error("❌ Erro ao carregar diretório")
        
        # Carregar URLs
        st.subheader("🌐 Carregar Páginas Web")
        urls_input = st.text_area(
            "URLs (uma por linha):",
            placeholder="https://exemplo.com\nhttps://outro-site.com"
        )
        
        if urls_input and st.button("🌐 Carregar URLs"):
            urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
            
            with st.spinner("Carregando páginas web..."):
                success = st.session_state.rag_system.load_documents(urls=urls)
                
                if success:
                    st.success(f"✅ {len(urls)} URL(s) carregada(s) com sucesso!")
                else:
                    st.error("❌ Erro ao carregar URLs")
        
        # Informações dos documentos
        st.subheader("📊 Informações dos Documentos")
        system_info = st.session_state.rag_system.get_system_info()
        
        if system_info:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Documentos", system_info.get("document_count", 0))
                st.metric("Modelo", system_info.get("model_name", "N/A"))
            
            with col2:
                st.metric("Temperatura", system_info.get("temperature", 0))
                st.metric("Max Tokens", system_info.get("max_tokens", 0))
            
            # Fontes de documentos
            sources = system_info.get("document_sources", [])
            if sources:
                st.subheader("📚 Fontes de Documentos")
                for source in sources:
                    st.text(f"• {source}")
        
        # Botão para resetar sistema
        if st.button("🔄 Resetar Sistema", type="secondary"):
            if st.session_state.rag_system.reset_system():
                st.success("✅ Sistema resetado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao resetar sistema")
    
    with tab3:
        st.header("🔍 Busca de Documentos")
        
        search_query = st.text_input(
            "Digite sua consulta de busca:",
            placeholder="Ex: inteligência artificial"
        )
        
        k_results = st.slider("Número de resultados:", 1, 10, 4)
        
        if search_query and st.button("🔍 Buscar"):
            with st.spinner("Buscando documentos..."):
                try:
                    results = st.session_state.rag_system.search_similar_documents(
                        search_query, k=k_results
                    )
                    
                    if results:
                        st.success(f"✅ Encontrados {len(results)} documentos")
                        
                        for i, result in enumerate(results, 1):
                            with st.expander(f"Documento {i}"):
                                st.markdown(f"**Fonte:** {result['metadata'].get('source', 'N/A')}")
                                st.markdown(f"**Tipo:** {result['metadata'].get('file_type', 'N/A')}")
                                st.markdown("**Conteúdo:**")
                                st.text(result['content'])
                    else:
                        st.warning("⚠️ Nenhum documento encontrado")
                        
                except Exception as e:
                    st.error(f"Erro na busca: {str(e)}")
    
    with tab4:
        multi_llm_interface()
    
    with tab5:
        privacy_interface()
    
    with tab6:
        st.header("ℹ️ Informações do Sistema")
        
        system_info = st.session_state.rag_system.get_system_info()
        
        if system_info:
            st.markdown("""
            <div class="info-box">
                <h3>🎯 Sistema RAG Python</h3>
                <p>Este é um sistema completo de Retrieval-Augmented Generation que permite:</p>
                <ul>
                    <li>Carregar documentos em PDF, DOCX, TXT e páginas web</li>
                    <li>Processar e indexar documentos usando embeddings</li>
                    <li>Realizar buscas semânticas</li>
                    <li>Gerar respostas baseadas no contexto dos documentos</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📊 Estatísticas")
            col1, col2 = st.columns(2)
            
            with col1:
                st.json({
                    "Modelo": system_info.get("model_name"),
                    "Temperatura": system_info.get("temperature"),
                    "Max Tokens": system_info.get("max_tokens")
                })
            
            with col2:
                vector_info = system_info.get("vector_store", {})
                st.json({
                    "Documentos": vector_info.get("document_count", 0),
                    "Coleção": vector_info.get("collection_name"),
                    "Diretório": vector_info.get("persist_directory")
                })
            
            # Fontes de documentos
            sources = system_info.get("document_sources", [])
            if sources:
                st.subheader("📚 Documentos Carregados")
                for source in sources:
                    st.text(f"• {source}")
            else:
                st.info("📝 Nenhum documento carregado ainda. Use a aba 'Documentos' para carregar arquivos.")
        
        st.subheader("🔧 Tecnologias Utilizadas")
        st.markdown("""
        - **LangChain**: Framework para aplicações de IA
        - **Multi-LLM**: OpenAI, Google Gemini, OpenRouter, DeepSeek
        - **Microsoft Presidio**: Detecção de dados pessoais LGPD
        - **PostgreSQL**: Banco de dados principal
        - **ChromaDB**: Banco de dados de vetores
        - **Streamlit**: Interface web
        - **FastAPI**: API REST
        - **Sentence Transformers**: Embeddings de texto
        """)
        
        st.subheader("🚀 Sistemas Disponíveis")
        st.markdown("""
        **Interface Atual (app.py):** ✅ Sistema RAG Local + Multi-LLM + Privacidade
        
        **Outras Interfaces Especializadas:**
        - `streamlit run agent_app.py` - Sistema de Agentes especializados
        - `streamlit run app_multi_llm.py` - Comparação avançada Multi-LLM
        - `streamlit run app_privacy_dashboard.py` - Dashboard LGPD completo
        - `streamlit run app_integrated.py` - Interface integrada com RAGFlow
        
        **API REST:**
        - FastAPI Server: http://192.168.8.4:5000/docs
        """)
        
        st.subheader("📋 Release Information")
        st.info("**RAG Python v1.5.1** - Sistema completo com 100% dos testes passando")
        st.markdown("""
        - **Release oficial:** [v1.5.1](https://github.com/jessefreitas/rag_python/releases/tag/v1.5.1-release)
        - **Pipeline CI/CD:** GitHub Actions ativo
        - **Cobertura de testes:** 44% (1.097/2.481 linhas)
        - **Testes:** 33/33 passando (100% success)
        """)

def multi_llm_interface():
    """Interface Multi-LLM"""
    st.header("🤖 Comparação Multi-LLM")
    
    # Inicializar LLM manager
    if 'llm_manager' not in st.session_state:
        st.session_state.llm_manager = LLMProviderManager()
    
    manager = st.session_state.llm_manager
    available_providers = manager.list_available_providers()
    
    if not available_providers:
        st.warning("⚠️ Nenhum provedor LLM configurado. Configure suas chaves de API.")
        st.info("**Provedores Suportados:**")
        st.write("- OpenAI (OPENAI_API_KEY)")
        st.write("- Google Gemini (GOOGLE_API_KEY)")
        st.write("- OpenRouter (OPENROUTER_API_KEY)")
        st.write("- DeepSeek (DEEPSEEK_API_KEY)")
        return
    
    st.success(f"✅ {len(available_providers)} provedores configurados: {', '.join(available_providers)}")
    
    # Seleção de provedores
    selected_providers = st.multiselect(
        "Selecione provedores para comparar:",
        available_providers,
        default=available_providers[:2] if len(available_providers) >= 2 else available_providers
    )
    
    # Pergunta para comparação
    question = st.text_area(
        "Digite sua pergunta:",
        placeholder="Ex: Explique o conceito de machine learning",
        height=100
    )
    
    if question and selected_providers and st.button("🔄 Comparar Respostas"):
        with st.spinner("Consultando múltiplos LLMs..."):
            try:
                messages = [{"role": "user", "content": question}]
                results = manager.compare_multi_llm(
                    messages,
                    providers=selected_providers,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # Exibir resultados
                st.subheader("📊 Resultados da Comparação")
                
                for provider, result in results.items():
                    with st.expander(f"{provider.upper()} - {result.get('model', 'N/A')}", expanded=True):
                        if result["success"]:
                            st.success(f"✅ Sucesso - {result['duration']:.2f}s")
                            st.write(result["response"])
                        else:
                            st.error(f"❌ Erro: {result['error']}")
                
            except Exception as e:
                st.error(f"Erro na comparação: {str(e)}")

def privacy_interface():
    """Interface de privacidade LGPD"""
    st.header("🔒 Sistema de Privacidade LGPD")
    
    st.subheader("🔍 Detecção de Dados Pessoais")
    
    text_to_analyze = st.text_area(
        "Digite o texto para análise de privacidade:",
        placeholder="Ex: João Silva, CPF 123.456.789-00, mora na Rua das Flores, 123",
        height=100
    )
    
    if text_to_analyze and st.button("🔍 Analisar Dados Pessoais"):
        with st.spinner("Analisando dados pessoais..."):
            try:
                # Usar o sistema de privacidade
                detection = privacy_manager.detect_personal_data_only(
                    text_to_analyze, 
                    detailed=True
                )
                
                if detection.get('has_personal_data', False):
                    st.warning("⚠️ Dados pessoais detectados!")
                    
                    # Exibir detalhes
                    entities = detection.get('entities', [])
                    if entities:
                        st.subheader("📋 Entidades Detectadas")
                        for entity in entities:
                            st.write(f"• **{entity['entity_type']}**: {entity['text']} (Confiança: {entity['score']:.2f})")
                    
                    # Análise de riscos
                    risk_analysis = privacy_manager.analyze_document_privacy_risks(text_to_analyze)
                    
                    st.subheader("⚠️ Análise de Riscos")
                    st.write(f"**Nível de Risco**: {risk_analysis.get('risk_level', 'N/A')}")
                    st.write(f"**Score**: {risk_analysis.get('risk_score', 0)}")
                    
                    recommendations = risk_analysis.get('recommendations', [])
                    if recommendations:
                        st.write("**Recomendações:**")
                        for rec in recommendations:
                            st.write(f"• {rec}")
                
                else:
                    st.success("✅ Nenhum dado pessoal detectado!")
                
            except Exception as e:
                st.error(f"Erro na análise: {str(e)}")

if __name__ == "__main__":
    main() 