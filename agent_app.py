"""
Interface Streamlit para Agentes de IA integrados com RAG
Permite interagir com diferentes tipos de agentes
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any

from agent_system import (
    MultiAgentSystem, 
    ConversationalAgent, 
    ResearchAgent, 
    TaskExecutorAgent,
    create_agent
)
from rag_system import RAGSystem
from ragflow_client import RAGFlowRAGSystem

# Configuração da página
st.set_page_config(
    page_title="Agentes RAG - Sistema Inteligente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .response-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #2ca02c;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #d62728;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_systems():
    """Inicializa os sistemas RAG e agentes"""
    try:
        # Verificar qual sistema RAG usar
        use_ragflow = st.session_state.get('use_ragflow', False)
        
        if use_ragflow:
            # Usar RAGFlow
            rag_system = RAGFlowRAGSystem(
                base_url=os.getenv("RAGFLOW_BASE_URL", "http://localhost:9380"),
                api_key=os.getenv("RAGFLOW_API_KEY")
            )
        else:
            # Usar RAG Python local
            rag_system = RAGSystem()
        
        # Criar sistema multi-agente
        multi_agent_system = MultiAgentSystem(rag_system)
        
        return rag_system, multi_agent_system
        
    except Exception as e:
        st.error(f"Erro ao inicializar sistemas: {str(e)}")
        return None, None

def display_agent_info(agent_name: str, agent_info: Dict[str, Any]):
    """Exibe informações do agente"""
    with st.expander(f"📋 Informações do Agente: {agent_name}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Nome:** {agent_info['name']}")
            st.write(f"**Descrição:** {agent_info['description']}")
            st.write(f"**Modelo:** {agent_info['model']}")
        
        with col2:
            st.write(f"**Temperatura:** {agent_info['temperature']}")
            st.write(f"**Memória:** {'Ativada' if agent_info['memory_enabled'] else 'Desativada'}")
            st.write(f"**Ferramentas:** {', '.join(agent_info['tools'])}")

def display_response(response, agent_name: str):
    """Exibe a resposta do agente"""
    st.markdown(f"### 🤖 Resposta do {agent_name}")
    
    # Exibir conteúdo principal
    st.markdown(f"""
    <div class="response-box">
        {response.content}
    </div>
    """, unsafe_allow_html=True)
    
    # Exibir metadados
    with st.expander("📊 Metadados da Resposta"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Confiança", f"{response.confidence:.2f}")
        
        with col2:
            st.metric("Ações Realizadas", len(response.actions_taken))
        
        with col3:
            st.metric("Fontes", len(response.sources))
        
        # Exibir ações realizadas
        if response.actions_taken:
            st.write("**Ações Realizadas:**")
            for action in response.actions_taken:
                st.write(f"• {action}")
        
        # Exibir fontes
        if response.sources:
            st.write("**Fontes:**")
            for source in response.sources:
                st.write(f"• {source}")
        
        # Exibir metadados completos
        st.write("**Metadados Completos:**")
        st.json(response.metadata)

def main():
    """Função principal da aplicação"""
    
    # Título principal
    st.title("🤖 Sistema de Agentes RAG")
    st.markdown("Sistema inteligente que combina agentes de IA com RAG para respostas baseadas em documentos")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Seleção do sistema RAG
        use_ragflow = st.checkbox(
            "Usar RAGFlow (API)",
            value=st.session_state.get('use_ragflow', False),
            help="Marque para usar RAGFlow via API em vez do RAG Python local"
        )
        st.session_state['use_ragflow'] = use_ragflow
        
        # Configurações de API
        if use_ragflow:
            st.subheader("🔗 Configurações RAGFlow")
            ragflow_url = st.text_input(
                "URL do RAGFlow",
                value=os.getenv("RAGFLOW_BASE_URL", "http://localhost:9380"),
                help="URL base da API do RAGFlow"
            )
            ragflow_key = st.text_input(
                "API Key do RAGFlow",
                value=os.getenv("RAGFLOW_API_KEY", ""),
                type="password",
                help="Chave de API do RAGFlow"
            )
            
            # Atualizar variáveis de ambiente
            os.environ["RAGFLOW_BASE_URL"] = ragflow_url
            os.environ["RAGFLOW_API_KEY"] = ragflow_key
        
        # Configurações do OpenAI
        st.subheader("🔑 Configurações OpenAI")
        openai_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Chave de API do OpenAI"
        )
        os.environ["OPENAI_API_KEY"] = openai_key
        
        # Botão para reinicializar sistemas
        if st.button("🔄 Reinicializar Sistemas"):
            st.cache_resource.clear()
            st.rerun()
    
    # Verificar se as chaves estão configuradas
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OpenAI API Key não configurada. Configure na sidebar.")
        return
    
    if use_ragflow and not os.getenv("RAGFLOW_API_KEY"):
        st.warning("⚠️ RAGFlow API Key não configurada. Configure na sidebar.")
    
    # Inicializar sistemas
    rag_system, multi_agent_system = initialize_systems()
    
    if not rag_system or not multi_agent_system:
        st.error("❌ Erro ao inicializar sistemas. Verifique as configurações.")
        return
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Conversa Inteligente", 
        "🔍 Pesquisa Avançada", 
        "⚡ Executor de Tarefas",
        "📊 Status do Sistema"
    ])
    
    # Tab 1: Conversa Inteligente
    with tab1:
        st.header("💬 Conversa Inteligente")
        st.markdown("Converse com o agente conversacional que usa RAG para respostas informadas")
        
        # Área de chat
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
        
        # Exibir histórico
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.write(f"👤 **Você:** {message['content']}")
            else:
                st.write(f"🤖 **Agente:** {message['content']}")
        
        # Input do usuário
        user_input = st.text_area(
            "Digite sua mensagem:",
            height=100,
            placeholder="Faça uma pergunta ou inicie uma conversa..."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.button("🚀 Enviar", type="primary")
        
        with col2:
            clear_button = st.button("🗑️ Limpar Histórico")
        
        if clear_button:
            st.session_state.conversation_history = []
            st.rerun()
        
        if send_button and user_input:
            with st.spinner("🤖 Processando..."):
                try:
                    # Processar com agente conversacional
                    response = multi_agent_system.agents["conversational"].process(user_input)
                    
                    # Adicionar ao histórico
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response.content,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Exibir resposta
                    display_response(response, "Conversacional")
                    
                except Exception as e:
                    st.error(f"Erro no processamento: {str(e)}")
    
    # Tab 2: Pesquisa Avançada
    with tab2:
        st.header("🔍 Pesquisa Avançada")
        st.markdown("Use o agente de pesquisa para análises detalhadas de documentos")
        
        # Input de pesquisa
        research_topic = st.text_input(
            "Tópico de pesquisa:",
            placeholder="Digite o tópico que deseja pesquisar nos documentos..."
        )
        
        if st.button("🔍 Iniciar Pesquisa", type="primary") and research_topic:
            with st.spinner("🔍 Realizando pesquisa..."):
                try:
                    # Usar agente de pesquisa
                    research_agent = multi_agent_system.agents["research"]
                    response = research_agent.analyze_documents(research_topic)
                    
                    # Exibir resultados
                    display_response(response, "Pesquisa")
                    
                except Exception as e:
                    st.error(f"Erro na pesquisa: {str(e)}")
    
    # Tab 3: Executor de Tarefas
    with tab3:
        st.header("⚡ Executor de Tarefas")
        st.markdown("Use o agente executor para realizar tarefas específicas baseadas nos documentos")
        
        # Seleção de tipo de tarefa
        task_type = st.selectbox(
            "Tipo de Tarefa:",
            [
                "Análise de Documento",
                "Resumo Executivo",
                "Extração de Informações",
                "Comparação de Documentos",
                "Recomendações",
                "Tarefa Personalizada"
            ]
        )
        
        # Input da tarefa
        if task_type == "Tarefa Personalizada":
            task_description = st.text_area(
                "Descrição da Tarefa:",
                height=150,
                placeholder="Descreva detalhadamente a tarefa que deseja executar..."
            )
        else:
            task_description = st.text_area(
                f"Detalhes da {task_type}:",
                height=150,
                placeholder=f"Descreva os detalhes para {task_type.lower()}..."
            )
        
        if st.button("⚡ Executar Tarefa", type="primary") and task_description:
            with st.spinner("⚡ Executando tarefa..."):
                try:
                    # Usar agente executor
                    executor_agent = multi_agent_system.agents["executor"]
                    response = executor_agent.execute_task(task_description)
                    
                    # Exibir resultados
                    display_response(response, "Executor")
                    
                except Exception as e:
                    st.error(f"Erro na execução: {str(e)}")
    
    # Tab 4: Status do Sistema
    with tab4:
        st.header("📊 Status do Sistema")
        
        # Status dos agentes
        st.subheader("🤖 Status dos Agentes")
        agent_status = multi_agent_system.get_agent_status()
        
        for agent_name, agent_info in agent_status.items():
            display_agent_info(agent_name, agent_info)
        
        # Métricas do sistema
        st.subheader("📈 Métricas do Sistema")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Agentes Ativos",
                len(multi_agent_system.agents),
                help="Número total de agentes disponíveis"
            )
        
        with col2:
            st.metric(
                "Sistema RAG",
                "RAGFlow" if use_ragflow else "RAG Python",
                help="Sistema RAG em uso"
            )
        
        with col3:
            st.metric(
                "Conversas",
                len(st.session_state.get("conversation_history", [])),
                help="Número de mensagens no histórico"
            )
        
        with col4:
            st.metric(
                "Status",
                "🟢 Ativo" if rag_system and multi_agent_system else "🔴 Inativo",
                help="Status geral do sistema"
            )
        
        # Informações do sistema
        st.subheader("ℹ️ Informações do Sistema")
        
        system_info = {
            "Sistema RAG": "RAGFlow (API)" if use_ragflow else "RAG Python (Local)",
            "Agentes Disponíveis": list(multi_agent_system.agents.keys()),
            "Memória Ativada": any(agent.config.memory for agent in multi_agent_system.agents.values()),
            "Ferramentas RAG": ["rag_query", "search_documents"],
            "Última Atualização": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.json(system_info)

if __name__ == "__main__":
    main() 