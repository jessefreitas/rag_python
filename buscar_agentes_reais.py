#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para buscar agentes reais do sistema RAG
"""

import json
import os

def buscar_agentes_reais():
    """Busca agentes reais do sistema"""
    try:
        print("🤖 BUSCANDO AGENTES REAIS DO SISTEMA...")
        print("=" * 50)
        
        # Tentar importar o sistema
        from app_completo_unificado import RAGSystemUnified
        
        # Inicializar sistema
        rag_system = RAGSystemUnified()
        
        # Buscar agentes
        agents = rag_system.agent_manager.get_all_agents()
        
        real_agents = []
        for agent in agents:
            try:
                # Contar documentos
                docs = rag_system.get_agent_documents(agent['id'])
                doc_count = len(docs) if docs else 0
            except:
                doc_count = 0
            
            real_agent = {
                'id': agent['id'],
                'name': f"🤖 {agent['name']}",
                'description': agent.get('description', 'Agente especializado'),
                'agent_type': agent.get('agent_type', 'geral'),
                'documents_count': doc_count
            }
            real_agents.append(real_agent)
            print(f"📋 {real_agent['name']} - {real_agent['documents_count']} documentos")
        
        print(f"\n📊 Total: {len(real_agents)} agentes encontrados")
        
        # Salvar em arquivo
        with open('agentes_reais.json', 'w', encoding='utf-8') as f:
            json.dump(real_agents, f, indent=2, ensure_ascii=False)
        print("✅ Agentes salvos em agentes_reais.json")
        
        return real_agents
        
    except Exception as e:
        print(f"❌ Erro ao buscar agentes reais: {e}")
        print("⚠️ Usando agentes padrão")
        
        # Agentes padrão
        default_agents = [
            {
                "id": "ae80adff-3ebd-4bc5-afbf-6e739df6d2fb",
                "name": "🏥 Agente Hospitalar",
                "description": "Especialista em documentos hospitalares",
                "agent_type": "hospitalar",
                "documents_count": 2
            },
            {
                "id": "05b9bd04-28bc-4a1c-aa76-a2161b1ed1ac",
                "name": "⚖️ Agente Jurídico",
                "description": "Especialista em contratos e documentos legais",
                "agent_type": "juridico",
                "documents_count": 1
            },
            {
                "id": "agente-geral",
                "name": "🤖 Agente Geral",
                "description": "Processamento geral de documentos",
                "agent_type": "geral",
                "documents_count": 0
            },
            {
                "id": "agente-tecnico",
                "name": "🔧 Agente Técnico",
                "description": "Análise de documentação técnica",
                "agent_type": "tecnico",
                "documents_count": 0
            }
        ]
        
        # Salvar agentes padrão
        with open('agentes_reais.json', 'w', encoding='utf-8') as f:
            json.dump(default_agents, f, indent=2, ensure_ascii=False)
        print("✅ Agentes padrão salvos em agentes_reais.json")
        
        return default_agents

if __name__ == "__main__":
    agentes = buscar_agentes_reais()
    print(f"\n🎯 {len(agentes)} agentes prontos para usar na extensão!") 