# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
API REST Completa - RAG Python v1.4.0
Servidor FastAPI com endpoints para todas as funcionalidades
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

# Imports do sistema
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from privacy_system import privacy_manager
from llm_providers import LLMProviderManager
from monitoring_system import get_system_health

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
    description="API REST completa para sistema RAG com privacidade LGPD",
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

# Inicializacao
llm_manager = LLMProviderManager()

def get_current_user():
    """Validacao de autenticacao simplificada"""
    return {"user_id": "user", "permissions": ["read", "write"]}

# Endpoints principais
@app.get("/health")
async def health_check():
    """Verifica saude do sistema"""
    try:
        health = get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def system_status():
    """Status geral do sistema"""
    return {
        "version": "1.4.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "privacy_system": "active",
            "llm_providers": len(llm_manager.get_available_providers())
        }
    }

@app.post("/privacy/detect")
async def detect_personal_data(request: DetectionRequest, user = Depends(get_current_user)):
    """Detecta dados pessoais no conteudo"""
    try:
        detection = privacy_manager.detect_personal_data_only(request.content, detailed=request.detailed)
        
        record_info = privacy_manager.create_detection_only_record(
            content=request.content,
            agent_id=f"api_user_{user['user_id']}",
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
async def analyze_privacy_risk(request: DetectionRequest, user = Depends(get_current_user)):
    """Analisa riscos de privacidade"""
    try:
        risk_analysis = privacy_manager.analyze_document_privacy_risks(request.content)
        return risk_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/query")
async def query_llm(request: LLMQueryRequest, user = Depends(get_current_user)):
    """Executa query em LLM"""
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
    try:
        providers = llm_manager.get_available_providers()
        return {"available_providers": providers, "total": len(providers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints para Extensão Chrome
@app.get("/api/v1/extension/health")
async def extension_health():
    """Health check para extensão Chrome"""
    return {
        "status": "ok",
        "version": "1.5.1",
        "timestamp": datetime.now().isoformat(),
        "message": "RAG Python API funcionando"
    }

@app.post("/api/v1/extension/scrape")
async def extension_scrape(request: dict):
    """Endpoint para receber dados da extensão Chrome"""
    try:
        url = request.get('url')
        content = request.get('content')
        title = request.get('title')
        
        if not url or not content:
            raise HTTPException(status_code=400, detail="URL e conteúdo são obrigatórios")
        
        # Processar conteúdo
        result = {
            "success": True,
            "message": "Conteúdo processado com sucesso",
            "data": {
                "url": url,
                "title": title,
                "content_length": len(content),
                "processed_at": datetime.now().isoformat()
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/extension/analyze")
async def extension_analyze(request: dict):
    """Analisa conteúdo da extensão com RAG"""
    try:
        content = request.get('content')
        question = request.get('question', 'Resuma este conteúdo')
        
        if not content:
            raise HTTPException(status_code=400, detail="Conteúdo é obrigatório")
        
        # Simular análise RAG
        response = f"Análise do conteúdo: {content[:200]}..."
        
        return {
            "success": True,
            "response": response,
            "question": question,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API REST - RAG Python v1.4.0")
    print("🌐 Host: http://192.168.8.4:5000")
    print("📊 Dashboard: http://192.168.8.4:5000/docs")
    print("🔍 Health Check: http://192.168.8.4:5000/health")
    
    uvicorn.run(
        "api_server:app",
        host="192.168.8.4",
        port=5000,
        reload=True,
        log_level="info"
    ) 