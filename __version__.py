"""
Versão do Sistema RAG Python
"""

# RAG Python - Versioning System
# Controle de versão semântico

__version__ = "1.4.0"
__version_info__ = (1, 4, 0)

# Histórico de versões
VERSION_HISTORY = {
    "1.0.0": "Sistema RAG básico com agentes",
    "1.1.0": "Extensão Chrome e interfaces múltiplas", 
    "1.2.0": "Sistema de privacidade básico",
    "1.3.0": "LGPD compliance completo + Multi-LLM + Monitoramento + CI/CD",
    "1.4.0": "API REST completa + Microsoft Presidio + Detecção avançada"
}

# Componentes da versão atual
CURRENT_FEATURES = [
    "Sistema RAG multi-modal",
    "4 Provedores LLM (OpenAI, Google, OpenRouter, DeepSeek)",
    "Sistema de Privacidade LGPD completo",
    "Detecção sem anonimização (detection_only)",
    "Microsoft Presidio integration",
    "API REST FastAPI completa",
    "5 Interfaces Streamlit",
    "Extensão Chrome funcional",
    "Sistema de agentes especializados",
    "Monitoramento em tempo real",
    "Pipeline CI/CD automatizado",
    "Testes automatizados completos",
    "Dashboard de compliance LGPD",
    "Detecção avançada de PII com ML"
]

# Status da versão
VERSION_STATUS = "stable"
RELEASE_DATE = "2024-12-22"
COMPATIBILITY = "Python 3.9+"

# Marcos do projeto
__build_date__ = "2025-06-22"

# Componentes principais
COMPONENTS = {
    "rag_system": "Sistema RAG Local",
    "ragflow_integration": "Integração RAGFlow", 
    "agent_system": "Sistema de Agentes Especializados",
    "privacy_system": "Sistema de Privacidade e Compliance LGPD",
    "multi_llm": "Sistema Multi-LLM (4 provedores)",
    "chrome_extension": "Extensão Chrome para Scraping",
    "web_interfaces": "Interfaces Streamlit Múltiplas",
    "monitoring": "Sistema de Monitoramento e Observabilidade",
    "ci_cd": "Pipeline CI/CD Automatizado"
}

def get_version():
    """Retorna versão formatada"""
    return f"RAG Python v{__version__} ({VERSION_STATUS})"

def get_full_info():
    """Retorna informações completas da versão"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "build_date": __build_date__,
        "status": VERSION_STATUS,
        "release_date": RELEASE_DATE,
        "compatibility": COMPATIBILITY,
        "features": CURRENT_FEATURES,
        "history": VERSION_HISTORY,
        "components": COMPONENTS
    }

def get_version_info():
    """Retorna informações detalhadas da versão"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "status": VERSION_STATUS,
        "release_date": RELEASE_DATE,
        "compatibility": COMPATIBILITY,
        "features": CURRENT_FEATURES,
        "history": VERSION_HISTORY
    } 