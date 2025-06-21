"""
Interface web Streamlit para o sistema RAG
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import logging
from typing import List, Dict, Any

from rag_system import RAGSystem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="RAG Python - Sistema de IA",
    page_icon="🤖",
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

@st.cache_resource
def initialize_rag_system():
    """Inicializa o sistema RAG com cache"""
    try:
        # Verificar se a API key está configurada
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("⚠️ OPENAI_API_KEY não configurada. Configure a variável de ambiente.")
            return None
        
        rag = RAGSystem()
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
    st.markdown('<h1 class="main-header">🤖 RAG Python - Sistema de IA</h1>', unsafe_allow_html=True)
    
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
        
        # Botão para atualizar configurações
        if st.button("🔄 Atualizar Configurações"):
            if 'rag_system' in st.session_state:
                success = st.session_state.rag_system.update_model_settings(
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                if success:
                    st.success("Configurações atualizadas!")
                else:
                    st.error("Erro ao atualizar configurações")
    
    # Inicializar sistema RAG
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = initialize_rag_system()
    
    if st.session_state.rag_system is None:
        st.error("❌ Sistema RAG não pôde ser inicializado. Verifique sua API key.")
        return
    
    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📁 Documentos", "🔍 Busca", "ℹ️ Informações"])
    
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
                st.metric("Documentos", system_info.get("vector_store", {}).get("document_count", 0))
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
        - **OpenAI**: Modelos de linguagem GPT
        - **ChromaDB**: Banco de dados de vetores
        - **Streamlit**: Interface web
        - **Sentence Transformers**: Embeddings de texto
        """)

if __name__ == "__main__":
    main() 