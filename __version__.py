"""
Versão do Sistema RAG Python
"""

__version__ = "1.2.0"
__version_info__ = (1, 2, 0)

# Marcos do projeto
__build_date__ = "2025-06-22"
__status__ = "stable"

# Componentes principais
COMPONENTS = {
    "rag_system": "Sistema RAG Local",
    "ragflow_integration": "Integração RAGFlow", 
    "agent_system": "Sistema de Agentes Especializados",
    "chrome_extension": "Extensão Chrome para Scraping",
    "web_interfaces": "Interfaces Streamlit Múltiplas"
}

def get_version():
    """Retorna versão formatada"""
    return f"RAG Python v{__version__} ({__status__})"

def get_full_info():
    """Retorna informações completas da versão"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "build_date": __build_date__,
        "status": __status__,
        "components": COMPONENTS
    } 