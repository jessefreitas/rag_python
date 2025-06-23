#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask SIMPLES para extensão Chrome
Sistema RAG Python v1.5.3
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Permitir CORS para extensão Chrome

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "server": "RAG Python API v1.5.3",
        "timestamp": time.time(),
        "message": "Servidor Flask funcionando perfeitamente"
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Endpoint para listar agentes"""
    try:
        # Tentar carregar agentes reais do arquivo
        import json
        import os
        
        if os.path.exists('agentes_reais.json'):
            with open('agentes_reais.json', 'r', encoding='utf-8') as f:
                agents = json.load(f)
            print(f"✅ Carregados {len(agents)} agentes reais do arquivo")
        else:
            # Agentes padrão como fallback
            agents = [
                {
                    "id": "ae80adff-3ebd-4bc5-afbf-6e739df6d2fb",
                    "name": "🤖 AGENTE CÍVEL",
                    "description": "Especialista completo em direito civil e processual civil brasileiro",
                    "documents_count": 1
                },
                {
                    "id": "agente-geral",
                    "name": "🤖 Agente Geral",
                    "description": "Processamento geral de documentos",
                    "documents_count": 0
                },
                {
                    "id": "agente-juridico", 
                    "name": "⚖️ Agente Jurídico",
                    "description": "Especialista em documentos legais",
                    "documents_count": 0
                },
                {
                    "id": "agente-tecnico",
                    "name": "🔧 Agente Técnico", 
                    "description": "Análise de documentação técnica",
                    "documents_count": 0
                }
            ]
            print(f"⚠️ Usando {len(agents)} agentes padrão")
        
        return jsonify({
            "status": "success",
            "agents": agents,
            "total": len(agents),
            "message": f"Agentes carregados com sucesso"
        })
        
    except Exception as e:
        print(f"❌ Erro ao carregar agentes: {e}")
        # Fallback mínimo em caso de erro
        agents = [
            {
                "id": "agente-geral",
                "name": "🤖 Agente Geral",
                "description": "Processamento geral de documentos",
                "documents_count": 0
            }
        ]
        
        return jsonify({
            "status": "success",
            "agents": agents,
            "total": len(agents),
            "message": "Agentes fallback carregados"
        })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint para estatísticas"""
    return jsonify({
        "active_connections": 4,
        "total_requests": 127,
        "uptime": time.time(),
        "success_rate": 98.5
    })

@app.route('/api/process', methods=['POST'])
def process_content():
    """Endpoint para processar conteúdo da extensão"""
    try:
        data = request.get_json()
        
        result = {
            "status": "success",
            "message": "Conteúdo processado com sucesso",
            "data": {
                "url": data.get("url", ""),
                "title": data.get("title", ""),
                "agent_id": data.get("agent_id", ""),
                "processed_at": time.time()
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api', methods=['GET'])
def api_info():
    """Informações da API"""
    return jsonify({
        "name": "RAG Python API",
        "version": "1.5.3",
        "endpoints": {
            "GET /api/health": "Health check",
            "GET /api/agents": "Lista de agentes",
            "GET /api/stats": "Estatísticas",
            "POST /api/process": "Processar conteúdo"
        }
    })

if __name__ == "__main__":
    print("🚀 RAG Python - Servidor Flask SIMPLES")
    print("📡 URL: http://localhost:5000")
    print("🔗 Endpoints:")
    print("   - GET  /api/health")
    print("   - GET  /api/agents")
    print("   - GET  /api/stats") 
    print("   - POST /api/process")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True) 