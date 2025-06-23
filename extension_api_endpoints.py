#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔌 ENDPOINTS API PARA EXTENSÃO CHROME
Sistema de endpoints para comunicação com a extensão Chrome
"""

import streamlit as st
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
from dataclasses import dataclass, asdict

# Estado global para conexões da extensão
if 'extension_connections' not in st.session_state:
    st.session_state.extension_connections = {}

if 'extension_stats' not in st.session_state:
    st.session_state.extension_stats = {
        'total_requests': 0,
        'successful_requests': 0,
        'failed_requests': 0,
        'active_connections': 0,
        'last_activity': None
    }

@dataclass
class ConnectionInfo:
    """Informações de uma conexão da extensão"""
    connection_id: str
    timestamp: float
    user_agent: str = "RAG-Control Extension"
    requests_count: int = 0
    last_activity: float = None
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = self.timestamp

class ExtensionAPI:
    """Gerenciador de API para extensão Chrome"""
    
    def __init__(self):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.total_requests = 0
        self.start_time = time.time()
    
    def register_connection(self, user_agent: str = "RAG-Control Extension") -> str:
        """Registra nova conexão da extensão"""
        connection_id = str(uuid.uuid4())[:8]
        self.connections[connection_id] = ConnectionInfo(
            connection_id=connection_id,
            timestamp=time.time(),
            user_agent=user_agent
        )
        return connection_id
    
    def update_activity(self, connection_id: str = None) -> str:
        """Atualiza atividade de uma conexão"""
        if not connection_id:
            connection_id = self.register_connection()
        
        if connection_id in self.connections:
            self.connections[connection_id].last_activity = time.time()
            self.connections[connection_id].requests_count += 1
        
        self.total_requests += 1
        return connection_id
    
    def get_health_status(self, connection_id: str = None) -> Dict[str, Any]:
        """Endpoint de health check"""
        connection_id = self.update_activity(connection_id)
        
        return {
            "status": "connected",
            "server": "RAG Python v1.5.3",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time,
            "connection_id": connection_id,
            "total_connections": len(self.connections),
            "total_requests": self.total_requests
        }
    
    def get_agents_list(self, connection_id: str = None) -> Dict[str, Any]:
        """Endpoint para listar agentes disponíveis"""
        connection_id = self.update_activity(connection_id)
        
        try:
            from agent_system import Agent
            agents = Agent.get_all()
            
            agents_data = []
            for agent in agents:
                agent_dict = agent.to_dict()
                agents_data.append({
                    "id": agent_dict.get("id"),
                    "name": agent_dict.get("name"),
                    "description": agent_dict.get("description"),
                    "type": agent_dict.get("agent_type", "general"),
                    "status": "active",
                    "documents_count": len(agent_dict.get("documents", []))
                })
            
            return {
                "status": "success",
                "connection_id": connection_id,
                "agents": agents_data,
                "total": len(agents_data),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "connection_id": connection_id,
                "message": f"Erro ao carregar agentes: {str(e)}",
                "agents": [],
                "total": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Estatísticas das conexões"""
        active_connections = []
        current_time = time.time()
        
        # Limpar conexões antigas (mais de 5 minutos)
        expired_connections = []
        for conn_id, conn in self.connections.items():
            if current_time - conn.last_activity > 300:  # 5 minutos
                expired_connections.append(conn_id)
            else:
                active_connections.append({
                    "id": conn.connection_id,
                    "duration": current_time - conn.timestamp,
                    "requests": conn.requests_count,
                    "last_activity": datetime.fromtimestamp(conn.last_activity).isoformat()
                })
        
        # Remover conexões expiradas
        for conn_id in expired_connections:
            del self.connections[conn_id]
        
        return {
            "active_connections": len(active_connections),
            "total_requests": self.total_requests,
            "uptime": current_time - self.start_time,
            "connections": active_connections,
            "success_rate": 95.5,  # Simulado
            "last_activity": datetime.now().isoformat() if active_connections else None
        }
    
    def process_extension_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa requisições da extensão"""
        if params is None:
            params = {}
        
        connection_id = params.get("connection_id")
        
        if endpoint == "health":
            return self.get_health_status(connection_id)
        elif endpoint == "agents":
            return self.get_agents_list(connection_id)
        elif endpoint == "stats":
            return self.get_connection_stats()
        else:
            return {
                "status": "error",
                "message": f"Endpoint desconhecido: {endpoint}",
                "timestamp": datetime.now().isoformat()
            }

# Instância global da API
extension_api = ExtensionAPI()

def handle_extension_request(endpoint: str, params: Dict[str, Any] = None) -> str:
    """Handler principal para requisições da extensão"""
    try:
        result = extension_api.process_extension_request(endpoint, params)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_response = {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)

def render_connection_dashboard():
    """Renderiza dashboard de conexões da extensão"""
    
    st.header("🔌 Conexões da Extensão Chrome")
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Conexões Ativas",
            st.session_state.extension_stats['active_connections'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Total de Requisições",
            st.session_state.extension_stats['total_requests'],
            delta=None
        )
    
    with col3:
        success_rate = 0
        if st.session_state.extension_stats['total_requests'] > 0:
            success_rate = round(
                (st.session_state.extension_stats['successful_requests'] / 
                 st.session_state.extension_stats['total_requests']) * 100, 1
            )
        st.metric("Taxa de Sucesso", f"{success_rate}%")
    
    with col4:
        last_activity = st.session_state.extension_stats.get('last_activity')
        if last_activity:
            time_diff = datetime.now() - last_activity
            if time_diff.seconds < 60:
                activity_text = "Agora"
            elif time_diff.seconds < 3600:
                activity_text = f"{time_diff.seconds // 60}m atrás"
            else:
                activity_text = f"{time_diff.seconds // 3600}h atrás"
        else:
            activity_text = "Nunca"
        
        st.metric("Última Atividade", activity_text)
    
    # Conexões ativas
    st.subheader("📡 Conexões Ativas")
    
    if not st.session_state.extension_connections:
        st.info("🔍 Nenhuma conexão ativa da extensão Chrome")
        st.markdown("""
        **Para conectar a extensão:**
        1. Instale a extensão Chrome v1.5.3
        2. Configure a URL do servidor: `http://localhost:8501`
        3. A conexão aparecerá aqui automaticamente
        """)
    else:
        for conn_id, conn_info in st.session_state.extension_connections.items():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**🔗 {conn_id[:8]}...**")
                    st.caption(f"Conectado em: {conn_info['connected_at'].strftime('%H:%M:%S')}")
                
                with col2:
                    st.write(f"**{conn_info['requests_count']}** requisições")
                    duration = datetime.now() - conn_info['connected_at']
                    st.caption(f"Duração: {str(duration).split('.')[0]}")
                
                with col3:
                    if conn_info['status'] == 'connected':
                        st.success("🟢 Conectado")
                    else:
                        st.error("🔴 Desconectado")
                
                st.divider()
    
    # Teste de conexão
    st.subheader("🧪 Teste de Conexão")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Simular Health Check", use_container_width=True):
            result = handle_extension_request('/health')
            if result['status'] == 'connected':
                st.success("✅ Health check bem-sucedido!")
                st.json(result)
            else:
                st.error("❌ Falha no health check")
                st.json(result)
    
    with col2:
        if st.button("📋 Listar Agentes", use_container_width=True):
            result = handle_extension_request('/agents')
            if result['status'] == 'success':
                st.success(f"✅ {result['total']} agentes encontrados")
                for agent in result['agents']:
                    st.write(f"- **{agent['name']}** ({agent['type']})")
            else:
                st.error("❌ Erro ao listar agentes")
                st.json(result)
    
    # Logs de atividade
    st.subheader("📊 Estatísticas Detalhadas")
    
    stats_data = {
        'Total de Requisições': st.session_state.extension_stats['total_requests'],
        'Requisições Bem-sucedidas': st.session_state.extension_stats['successful_requests'],
        'Requisições Falhadas': st.session_state.extension_stats['failed_requests'],
        'Conexões Ativas': st.session_state.extension_stats['active_connections']
    }
    
    st.json(stats_data)
    
    # Botão para limpar estatísticas
    if st.button("🗑️ Limpar Estatísticas", type="secondary"):
        st.session_state.extension_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'active_connections': 0,
            'last_activity': None
        }
        st.session_state.extension_connections = {}
        st.rerun()

if __name__ == "__main__":
    render_connection_dashboard() 