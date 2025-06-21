"""
Interface web Streamlit integrada - RAG Python + RAGFlow
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import logging
from typing import List, Dict, Any

# Importar ambos os sistemas
from rag_system import RAGSystem
from ragflow_client import RAGFlowRAGSystem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="RAG Python + RAGFlow - Sistema Integrado",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Função principal da aplicação"""
    
    # Cabeçalho
    st.title("🤖 RAG Python + RAGFlow - Sistema Integrado")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Seletor de sistema
        st.subheader("🔧 Sistema Backend")
        system_type = st.selectbox(
            "Escolha o sistema:",
            ["rag_python", "ragflow"],
            index=0,
            help="RAG Python: Sistema local. RAGFlow: Sistema via API"
        )
        
        # Configurações específicas do RAGFlow
        if system_type == "ragflow":
            st.subheader("🌐 Configurações RAGFlow")
            
            ragflow_url = st.text_input(
                "URL do RAGFlow:",
                value=st.session_state.get('ragflow_url', 'http://localhost:8000'),
                help="URL da API do RAGFlow"
            )
            st.session_state['ragflow_url'] = ragflow_url
            
            collection_name = st.text_input(
                "Nome da Coleção:",
                value=st.session_state.get('collection_name', 'rag_python_docs'),
                help="Nome da coleção no RAGFlow"
            )
            st.session_state['collection_name'] = collection_name
        
        # Configuração da API OpenAI (para RAG Python)
        if system_type == "rag_python":
            st.subheader("🔑 Configuração OpenAI")
            api_key = st.text_input(
                "OpenAI API Key",
                value=os.getenv("OPENAI_API_KEY", ""),
                type="password",
                help="Sua chave da API OpenAI"
            )
            
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
    
    # Exibir seletor de sistema
    system_names = {
        "rag_python": "RAG Python (Local)",
        "ragflow": "RAGFlow (API)"
    }
    
    st.info(f"🔧 Sistema Ativo: {system_names.get(system_type, system_type)}")
    
    # Inicializar sistema RAG
    if 'rag_system' not in st.session_state or st.session_state.get('current_system') != system_type:
        try:
            if system_type == "rag_python":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    st.error("⚠️ OPENAI_API_KEY não configurada.")
                    return
                st.session_state.rag_system = RAGSystem()
            else:
                ragflow_url = st.session_state.get('ragflow_url', 'http://localhost:8000')
                collection_name = st.session_state.get('collection_name', 'rag_python_docs')
                st.session_state.rag_system = RAGFlowRAGSystem(ragflow_url, collection_name)
            
            st.session_state.current_system = system_type
        except Exception as e:
            st.error(f"Erro ao inicializar sistema: {str(e)}")
            return
    
    if st.session_state.rag_system is None:
        st.error("❌ Sistema RAG não pôde ser inicializado.")
        return
    
    # Abas principais
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📁 Documentos", "ℹ️ Informações"])
    
    with tab1:
        st.header("💬 Chat com IA")
        
        # Inicializar histórico de chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Exibir histórico de mensagens
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f"👤 **Você:** {message['content']}")
            else:
                st.write(f"🤖 **Assistente:** {message['content']}")
                if message.get("sources"):
                    st.write("📚 **Fontes:**")
                    for source in message["sources"]:
                        st.write(f"- {source.get('source', 'N/A')}")
        
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
        
        if system_type == "rag_python":
            # Upload de arquivos para RAG Python
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
        
        elif system_type == "ragflow":
            # Upload de arquivos para RAGFlow
            st.subheader("📤 Upload para RAGFlow")
            st.info("💡 Para RAGFlow, use a interface web do RAGFlow para upload de documentos.")
            
            uploaded_files = st.file_uploader(
                "Selecione arquivos para enviar ao RAGFlow",
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                if st.button("📥 Enviar para RAGFlow"):
                    with st.spinner("Enviando documentos para RAGFlow..."):
                        temp_dir = tempfile.mkdtemp()
                        
                        # Salvar arquivos temporariamente
                        file_paths = []
                        for uploaded_file in uploaded_files:
                            file_path = Path(temp_dir) / uploaded_file.name
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            file_paths.append(str(file_path))
                        
                        # Enviar para RAGFlow
                        success = st.session_state.rag_system.load_documents(file_paths)
                        
                        if success:
                            st.success(f"✅ {len(uploaded_files)} arquivo(s) enviado(s) para RAGFlow!")
                        else:
                            st.error("❌ Erro ao enviar arquivos para RAGFlow")
        
        # Informações dos documentos
        st.subheader("📊 Informações dos Documentos")
        system_info = st.session_state.rag_system.get_system_info()
        
        if system_info:
            if system_type == "rag_python":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Documentos", system_info.get("vector_store", {}).get("document_count", 0))
                    st.metric("Modelo", system_info.get("model_name", "N/A"))
                
                with col2:
                    st.metric("Temperatura", system_info.get("temperature", 0))
                    st.metric("Max Tokens", system_info.get("max_tokens", 0))
            
            elif system_type == "ragflow":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Status", system_info.get("ragflow_status", "N/A"))
                    st.metric("Documentos", system_info.get("document_count", 0))
                
                with col2:
                    st.metric("Coleção", system_info.get("collection_name", "N/A"))
                    st.metric("URL", system_info.get("ragflow_url", "N/A"))
    
    with tab3:
        st.header("ℹ️ Informações do Sistema")
        
        system_info = st.session_state.rag_system.get_system_info()
        
        if system_info:
            if system_type == "rag_python":
                st.info("🎯 Sistema RAG Python - Sistema local com LangChain, OpenAI, ChromaDB")
            else:
                st.info("🎯 Sistema RAGFlow - Sistema robusto via API com processamento avançado")
            
            st.subheader("📊 Estatísticas")
            st.json(system_info)
        
        st.subheader("🔧 Tecnologias Utilizadas")
        if system_type == "rag_python":
            st.markdown("""
            - **LangChain**: Framework para aplicações de IA
            - **OpenAI**: Modelos de linguagem GPT
            - **ChromaDB**: Banco de dados de vetores
            - **Streamlit**: Interface web
            """)
        else:
            st.markdown("""
            - **RAGFlow**: Plataforma RAG completa
            - **API REST**: Comunicação via HTTP
            - **Streamlit**: Interface web
            - **Backend Distribuído**: Escalabilidade e performance
            """)

if __name__ == "__main__":
    main() 