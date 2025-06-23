#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 HANDLER HTTP PARA EXTENSÃO CHROME
Sistema de endpoints HTTP para comunicação com extensão Chrome via Streamlit
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, Any
from extension_api_endpoints import extension_api, handle_extension_request

def handle_api_requests():
    """
    Processa requisições de API via query parameters
    Usado pela extensão Chrome para conectar ao sistema
    """
    
    # Verificar se há parâmetros de API na URL
    query_params = st.query_params
    
    if 'api' in query_params:
        api_endpoint = query_params['api']
        
        # Extrair parâmetros adicionais
        connection_id = query_params.get('connection_id', None)
        
        # Processar diferentes endpoints
        if api_endpoint == 'health':
            # Health check endpoint
            result = extension_api.get_health_status(connection_id)
            
            # Retornar JSON diretamente
            st.json(result)
            st.stop()
            
        elif api_endpoint == 'agents':
            # Agentes endpoint
            result = extension_api.get_agents_list(connection_id)
            
            # Retornar JSON diretamente
            st.json(result)
            st.stop()
            
        elif api_endpoint == 'stats':
            # Estatísticas endpoint
            result = extension_api.get_connection_stats()
            
            # Retornar JSON diretamente
            st.json(result)
            st.stop()
            
        else:
            # Endpoint não encontrado
            error_result = {
                "status": "error",
                "message": f"Endpoint não encontrado: {api_endpoint}",
                "available_endpoints": ["health", "agents", "stats"]
            }
            
            st.json(error_result)
            st.stop()

def setup_api_endpoints():
    """
    Configura os endpoints de API no início da aplicação
    """
    
    # Verificar se é uma requisição de API
    query_params = st.query_params
    
    if 'api' in query_params:
        # Configurar headers para JSON
        st.set_page_config(
            page_title="RAG API",
            page_icon="🔌",
            layout="centered"
        )
        
        # Processar requisição de API
        handle_api_requests()
    
    return False  # Não é uma requisição de API

def render_api_documentation():
    """
    Renderiza documentação da API para desenvolvedores
    """
    
    st.markdown("## 🔌 API Endpoints para Extensão Chrome")
    st.markdown("---")
    
    # Health Check
    st.markdown("### 🏥 Health Check")
    st.code("GET /?api=health&connection_id=opcional")
    st.markdown("Verifica se o servidor está funcionando e registra/atualiza conexão.")
    
    with st.expander("Exemplo de Resposta - Health Check"):
        example_health = {
            "status": "connected",
            "server": "RAG Python v1.5.3",
            "timestamp": "2025-06-23T01:30:00",
            "uptime": 3600.5,
            "connection_id": "abc123",
            "total_connections": 2,
            "total_requests": 15
        }
        st.json(example_health)
    
    # Agentes
    st.markdown("### 👥 Lista de Agentes")
    st.code("GET /?api=agents&connection_id=opcional")
    st.markdown("Retorna lista de agentes disponíveis no sistema.")
    
    with st.expander("Exemplo de Resposta - Agentes"):
        example_agents = {
            "status": "success",
            "connection_id": "abc123",
            "agents": [
                {
                    "id": "agent-001",
                    "name": "Agente Jurídico",
                    "description": "Especialista em direito civil",
                    "type": "specialized",
                    "status": "active",
                    "documents_count": 5
                }
            ],
            "total": 1,
            "timestamp": "2025-06-23T01:30:00"
        }
        st.json(example_agents)
    
    # Estatísticas
    st.markdown("### 📊 Estatísticas de Conexão")
    st.code("GET /?api=stats")
    st.markdown("Retorna estatísticas das conexões ativas.")
    
    with st.expander("Exemplo de Resposta - Estatísticas"):
        example_stats = {
            "active_connections": 2,
            "total_requests": 15,
            "uptime": 3600.5,
            "connections": [
                {
                    "id": "abc123",
                    "duration": 1800.0,
                    "requests": 8,
                    "last_activity": "2025-06-23T01:30:00"
                }
            ],
            "success_rate": 95.5,
            "last_activity": "2025-06-23T01:30:00"
        }
        st.json(example_stats)
    
    # URLs de Teste
    st.markdown("### 🔧 URLs de Teste")
    
    base_url = "http://localhost:8501"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Health Check:**")
        health_url = f"{base_url}/?api=health"
        st.code(health_url)
        if st.button("🏥 Testar Health", key="test_health"):
            st.markdown(f"[Abrir Health Check]({health_url})")
    
    with col2:
        st.markdown("**Agentes:**")
        agents_url = f"{base_url}/?api=agents"
        st.code(agents_url)
        if st.button("👥 Testar Agentes", key="test_agents"):
            st.markdown(f"[Abrir Agentes]({agents_url})")
    
    with col3:
        st.markdown("**Estatísticas:**")
        stats_url = f"{base_url}/?api=stats"
        st.code(stats_url)
        if st.button("📊 Testar Stats", key="test_stats"):
            st.markdown(f"[Abrir Estatísticas]({stats_url})")

if __name__ == "__main__":
    st.title("🔌 RAG Python - API Handler")
    render_api_documentation() 