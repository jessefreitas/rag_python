"""
Middleware de API para interceptar requisições da extensão Chrome
Sistema RAG Python v1.5.3
"""

import streamlit as st
import json
from urllib.parse import urlparse, parse_qs

def intercept_api_request():
    """
    Intercepta requisições de API no início da aplicação
    Retorna True se for uma requisição de API, False caso contrário
    """
    
    # Verificar query parameters
    try:
        query_params = st.query_params
        
        if 'api' in query_params:
            api_endpoint = query_params['api']
            connection_id = query_params.get('connection_id', None)
            
            # Importar API apenas quando necessário
            from extension_api_endpoints import extension_api
            
            # Processar endpoint
            if api_endpoint == 'health':
                result = extension_api.get_health_status(connection_id)
            elif api_endpoint == 'agents':
                result = extension_api.get_agents_list(connection_id)
            elif api_endpoint == 'stats':
                result = extension_api.get_connection_stats()
            else:
                result = {
                    "status": "error",
                    "message": f"Endpoint não encontrado: {api_endpoint}",
                    "available_endpoints": ["health", "agents", "stats"]
                }
            
            # Configurar página para API
            st.set_page_config(
                page_title="RAG API",
                page_icon="🔌",
                layout="centered"
            )
            
            # Mostrar resultado JSON
            st.markdown("### 🔌 RAG Python API")
            st.markdown(f"**Endpoint:** `{api_endpoint}`")
            st.json(result)
            
            # Parar execução
            st.stop()
            
        return False
        
    except Exception as e:
        # Se houver erro, continuar normalmente
        return False

# Executar interceptação no import
if __name__ != "__main__":
    # Só interceptar quando importado, não quando executado diretamente
    intercept_api_request() 