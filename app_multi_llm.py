#!/usr/bin/env python3
"""
Interface Streamlit para Sistema Multi-LLM
Comparação e teste de múltiplos provedores de IA
"""

import streamlit as st
import pandas as pd
import json
import time
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from llm_providers import LLMProviderManager

# Configuração da página
st.set_page_config(
    page_title="Multi-LLM Comparator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Inicializa o estado da sessão"""
    if 'llm_manager' not in st.session_state:
        st.session_state.llm_manager = LLMProviderManager()
    
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def sidebar_config():
    """Configurações da barra lateral"""
    st.sidebar.title("🛠️ Configurações")
    
    manager = st.session_state.llm_manager
    available_providers = manager.list_available_providers()
    
    if not available_providers:
        st.sidebar.error("❌ Nenhum provedor configurado!")
        st.sidebar.info("Configure suas chaves de API nas variáveis de ambiente")
        return None, None, None
    
    # Seleção de provedores para comparação
    selected_providers = st.sidebar.multiselect(
        "Provedores para comparação:",
        available_providers,
        default=available_providers[:2]  # Seleciona os primeiros 2 por padrão
    )
    
    # Configurações dos parâmetros
    st.sidebar.subheader("⚙️ Parâmetros")
    
    temperature = st.sidebar.slider(
        "Temperature",
        0.0, 2.0, 0.7, 0.1,
        help="Controla a criatividade das respostas"
    )
    
    max_tokens = st.sidebar.number_input(
        "Max Tokens",
        100, 4000, 1000, 100,
        help="Máximo de tokens na resposta"
    )
    
    return selected_providers, temperature, max_tokens

def display_provider_info():
    """Exibe informações dos provedores"""
    st.header("📋 Provedores Configurados")
    
    manager = st.session_state.llm_manager
    info = manager.get_provider_info()
    
    if info["providers"]:
        # Cria DataFrame para exibição
        providers_data = []
        for name, provider_info in info["providers"].items():
            providers_data.append({
                "Provedor": name.title(),
                "Modelo": provider_info["model_name"],
                "Temperature": provider_info["temperature"],
                "Max Tokens": provider_info["max_tokens"],
                "Status": "✅ Ativo" if name == info["active_provider"] else "⭕ Disponível"
            })
        
        df = pd.DataFrame(providers_data)
        st.dataframe(df, use_container_width=True)
        
        # Botões para ativar provedor
        st.subheader("🔄 Trocar Provedor Ativo")
        cols = st.columns(len(info["providers"]))
        
        for idx, provider_name in enumerate(info["providers"].keys()):
            with cols[idx]:
                if st.button(f"Ativar {provider_name.title()}", key=f"activate_{provider_name}"):
                    manager.set_active_provider(provider_name)
                    st.success(f"Provedor {provider_name.title()} ativado!")
                    st.rerun()
    else:
        st.warning("Nenhum provedor configurado")

def multi_llm_comparison():
    """Interface para comparação multi-LLM"""
    st.header("🔄 Comparação Multi-LLM")
    
    selected_providers, temperature, max_tokens = sidebar_config()
    
    if not selected_providers:
        st.warning("Selecione pelo menos um provedor na barra lateral")
        return
    
    # Campo de entrada para pergunta
    question = st.text_area(
        "Digite sua pergunta:",
        placeholder="Ex: Explique o que é inteligência artificial...",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        compare_button = st.button("🚀 Comparar Respostas", type="primary")
    
    with col2:
        if st.button("📊 Ver Última Comparação") and st.session_state.comparison_results:
            display_comparison_results(st.session_state.comparison_results)
    
    if compare_button and question:
        with st.spinner("Consultando LLMs..."):
            messages = [{"role": "user", "content": question}]
            
            manager = st.session_state.llm_manager
            results = manager.compare_multi_llm(
                messages,
                providers=selected_providers,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            st.session_state.comparison_results = results
            display_comparison_results(results)

def display_comparison_results(results: Dict[str, Any]):
    """Exibe resultados da comparação"""
    st.subheader("📊 Resultados da Comparação")
    
    # Métricas de performance
    successful_providers = [p for p, r in results.items() if r["success"]]
    failed_providers = [p for p, r in results.items() if not r["success"]]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Sucessos", len(successful_providers))
    with col2:
        st.metric("❌ Falhas", len(failed_providers))
    with col3:
        if successful_providers:
            avg_time = sum(results[p]["duration"] for p in successful_providers) / len(successful_providers)
            st.metric("⏱️ Tempo Médio", f"{avg_time:.2f}s")
    
    # Gráfico de performance
    if successful_providers:
        performance_data = []
        for provider in successful_providers:
            performance_data.append({
                "Provedor": provider.title(),
                "Tempo (s)": results[provider]["duration"],
                "Modelo": results[provider]["model"]
            })
        
        df_perf = pd.DataFrame(performance_data)
        
        fig = px.bar(
            df_perf, 
            x="Provedor", 
            y="Tempo (s)", 
            title="⏱️ Tempo de Resposta por Provedor",
            color="Tempo (s)",
            text="Modelo"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Respostas detalhadas
    st.subheader("🤖 Respostas dos LLMs")
    
    for provider_name, result in results.items():
        with st.expander(f"{provider_name.title()} ({result.get('model', 'N/A')})", expanded=True):
            if result["success"]:
                st.success(f"✅ Sucesso - {result['duration']}s")
                st.markdown(f"**Resposta:**\n{result['response']}")
                
                # Informações técnicas
                with st.expander("ℹ️ Detalhes Técnicos"):
                    st.json(result["provider_info"])
            else:
                st.error(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")

def chat_interface():
    """Interface de chat com LLM selecionado"""
    st.header("💬 Chat com LLM")
    
    manager = st.session_state.llm_manager
    available_providers = manager.list_available_providers()
    
    if not available_providers:
        st.error("Nenhum provedor disponível")
        return
    
    # Seleção do provedor
    selected_provider = st.selectbox(
        "Escolha o provedor:",
        available_providers,
        index=0 if available_providers else None
    )
    
    # Histórico do chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Campo de entrada
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Adiciona mensagem do usuário
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gera resposta
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    manager.set_active_provider(selected_provider)
                    
                    messages = []
                    for msg in st.session_state.chat_history:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    response = manager.generate_response(messages)
                    
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Erro ao gerar resposta: {e}")
    
    # Botão para limpar histórico
    if st.button("🗑️ Limpar Chat"):
        st.session_state.chat_history = []
        st.rerun()

def task_recommendations():
    """Recomendações de tarefas por LLM"""
    st.header("🎯 Recomendações por Tarefa")
    
    manager = st.session_state.llm_manager
    
    tasks = {
        "general": "Perguntas Gerais",
        "coding": "Programação",
        "creative": "Criatividade",
        "analysis": "Análise de Dados",
        "legal": "Questões Jurídicas"
    }
    
    recommendations_data = []
    for task_key, task_name in tasks.items():
        best_provider = manager.get_best_provider_for_task(task_key)
        recommendations_data.append({
            "Tarefa": task_name,
            "Provedor Recomendado": best_provider.title() if best_provider else "N/A",
            "Disponível": "✅" if best_provider and best_provider in manager.providers else "❌"
        })
    
    df_rec = pd.DataFrame(recommendations_data)
    st.dataframe(df_rec, use_container_width=True)
    
    # Gráfico de recomendações
    available_count = len([r for r in recommendations_data if r["Disponível"] == "✅"])
    
    fig = go.Figure(data=[
        go.Pie(
            labels=["Disponíveis", "Indisponíveis"],
            values=[available_count, len(recommendations_data) - available_count],
            hole=0.3
        )
    ])
    
    fig.update_layout(title="📊 Status das Recomendações")
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Função principal da aplicação"""
    init_session_state()
    
    st.title("🤖 Sistema Multi-LLM Comparator")
    st.markdown("**Compare diferentes modelos de IA e escolha o melhor para cada tarefa**")
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Provedores", 
        "🔄 Comparação", 
        "💬 Chat", 
        "🎯 Recomendações"
    ])
    
    with tab1:
        display_provider_info()
    
    with tab2:
        multi_llm_comparison()
    
    with tab3:
        chat_interface()
    
    with tab4:
        task_recommendations()
    
    # Footer
    st.markdown("---")
    st.markdown("**Desenvolvido para o projeto RAG Python** | 🚀 Multi-LLM System")

if __name__ == "__main__":
    main() 