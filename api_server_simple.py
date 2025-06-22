# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
API REST Simplificada - RAG Python v1.4.0
Servidor FastAPI com endpoints básicos
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

# Imports do sistema
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from privacy_system import privacy_manager
    PRIVACY_AVAILABLE = True
except ImportError:
    PRIVACY_AVAILABLE = False

try:
    from llm_providers import LLMProviderManager
    llm_manager = LLMProviderManager()
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Modelos Pydantic
class DetectionRequest(BaseModel):
    content: str = Field(..., description="Conteudo para detectar dados pessoais")
    detailed: bool = Field(True, description="Retornar analise detalhada")

class LLMQueryRequest(BaseModel):
    query: str = Field(..., description="Query para o LLM")
    provider: str = Field("openai", description="Provedor LLM")

# Configuracao do FastAPI
app = FastAPI(
    title="RAG Python API",
    description="API REST simplificada para sistema RAG com privacidade LGPD",
    version="1.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuracao CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints principais
@app.get("/health")
async def health_check():
    """Verifica saude do sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.4.0",
        "privacy_system": PRIVACY_AVAILABLE,
        "llm_system": LLM_AVAILABLE
    }

@app.get("/status")
async def system_status():
    """Status geral do sistema"""
    return {
        "version": "1.4.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "privacy_system": "active" if PRIVACY_AVAILABLE else "unavailable",
            "llm_providers": len(llm_manager.get_available_providers()) if LLM_AVAILABLE else 0
        }
    }

@app.post("/privacy/detect")
async def detect_personal_data(request: DetectionRequest):
    """Detecta dados pessoais no conteudo"""
    if not PRIVACY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sistema de privacidade nao disponivel")
    
    try:
        detection = privacy_manager.detect_personal_data_only(request.content, detailed=request.detailed)
        
        record_info = privacy_manager.create_detection_only_record(
            content=request.content,
            agent_id="api_user_simple",
            purpose="API detection request"
        )
        
        return {
            "detection": detection,
            "record_id": record_info['record_id'],
            "original_content_preserved": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/privacy/analyze-risk")
async def analyze_privacy_risk(request: DetectionRequest):
    """Analisa riscos de privacidade"""
    if not PRIVACY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sistema de privacidade nao disponivel")
    
    try:
        risk_analysis = privacy_manager.analyze_document_privacy_risks(request.content)
        return risk_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/query")
async def query_llm(request: LLMQueryRequest):
    """Executa query em LLM"""
    if not LLM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sistema LLM nao disponivel")
    
    try:
        response, response_time = llm_manager.query_provider(request.provider, request.query)
        
        return {
            "response": response,
            "provider": request.provider,
            "response_time": response_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/llm/providers")
async def list_providers():
    """Lista provedores LLM disponiveis"""
    if not LLM_AVAILABLE:
        return {"available_providers": [], "total": 0, "status": "LLM system unavailable"}
    
    try:
        providers = llm_manager.get_available_providers()
        return {"available_providers": providers, "total": len(providers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    return {
        "message": "API RAG Python v1.4.0 funcionando!",
        "timestamp": datetime.now().isoformat(),
        "test": "success"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API REST Simplificada - RAG Python v1.4.0")
    print("🌐 Host: http://192.168.8.4:5000")
    print("📊 Dashboard: http://192.168.8.4:5000/docs")
    print("🔍 Health Check: http://192.168.8.4:5000/health")
    print("🧪 Test Endpoint: http://192.168.8.4:5000/test")
    
    uvicorn.run(
        "api_server_simple:app",
        host="192.168.8.4",
        port=5000,
        reload=True,
        log_level="info"
    ) 