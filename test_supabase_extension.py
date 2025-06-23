#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da Extensão Chrome com Supabase Real - Porta 5002
"""

import requests
import json
import sys
from dotenv import load_dotenv

load_dotenv()

# URL do servidor na porta 5002
API_BASE_URL = 'http://localhost:5002'

def test_api_health():
    """Testa o endpoint de saúde"""
    print("🔍 Testando /api/health...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/health', timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check OK")
            print(f"Supabase: {data.get('supabase', 'unknown')}")
            print(f"Port: {data.get('port', 'unknown')}")
            return True
        else:
            print("❌ Health check falhou")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_api_agents():
    """Testa o endpoint de agentes"""
    print("\n🔍 Testando /api/agents...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/agents', timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Agentes carregados")
            print(f"Total: {data.get('total', 0)}")
            print(f"Source: {data.get('source', 'unknown')}")
            
            agents = data.get('agents', [])
            for i, agent in enumerate(agents[:3]):  # Mostrar só 3 primeiros
                print(f"  {i+1}. {agent.get('name')} (ID: {agent.get('id')}) - {agent.get('document_count', 0)} docs")
            
            return agents
        else:
            print(f"❌ Erro ao buscar agentes: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erro ao buscar agentes: {e}")
        return []

def test_api_stats():
    """Testa o endpoint de estatísticas"""
    print("\n🔍 Testando /api/stats...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/stats', timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Estatísticas carregadas")
            stats = data.get('stats', {})
            print(f"Total agentes: {stats.get('total_agents', 0)}")
            print(f"Total documentos: {stats.get('total_documents', 0)}")
            print(f"Source: {data.get('source', 'unknown')}")
            return True
        else:
            print(f"❌ Erro ao buscar estatísticas: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao buscar estatísticas: {e}")
        return False

def test_api_process(agents):
    """Testa o endpoint de processamento"""
    print("\n🔍 Testando /api/process...")
    
    # Usar primeiro agente disponível
    agent_id = agents[0]['id'] if agents else 'default'
    
    # Dados de teste
    test_data = {
        'agent_id': agent_id,
        'url': 'https://test.example.com',
        'title': 'Teste da Extensão Chrome',
        'content': 'Este é um conteúdo de teste para verificar se a extensão Chrome consegue salvar documentos no Supabase PostgreSQL.'
    }
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/api/process',
            json=test_data,
            timeout=15
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Conteúdo processado com sucesso")
                print(f"Agent ID: {data.get('agent_id')}")
                print(f"Content length: {data.get('content_length')}")
                return True
            else:
                print(f"❌ Falha no processamento: {data.get('error')}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao processar conteúdo: {e}")
        return False

def main():
    print("🧪 TESTE COMPLETO - EXTENSÃO CHROME + SUPABASE (PORTA 5002)")
    print("=" * 70)
    
    # Teste 1: Health check
    health_ok = test_api_health()
    
    # Teste 2: Buscar agentes
    agents = test_api_agents()
    
    # Teste 3: Estatísticas
    stats_ok = test_api_stats()
    
    # Teste 4: Processar conteúdo (só se tiver agentes)
    process_ok = False
    if agents:
        process_ok = test_api_process(agents)
    else:
        print("\n⚠️ Pulando teste de processamento - nenhum agente disponível")
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES:")
    print(f"Health Check: {'✅ OK' if health_ok else '❌ FALHOU'}")
    print(f"Agentes: {'✅ OK' if agents else '❌ FALHOU'} ({len(agents)} encontrados)")
    print(f"Estatísticas: {'✅ OK' if stats_ok else '❌ FALHOU'}")
    print(f"Processamento: {'✅ OK' if process_ok else '❌ FALHOU'}")
    
    all_ok = health_ok and bool(agents) and stats_ok and process_ok
    print(f"\n🎯 RESULTADO FINAL: {'✅ TODOS OS TESTES PASSARAM' if all_ok else '❌ ALGUNS TESTES FALHARAM'}")
    
    if all_ok:
        print("\n🎉 A extensão Chrome está pronta para usar!")
        print(f"🔗 Conecte-se ao servidor em: {API_BASE_URL}")
        print("📋 Agentes disponíveis para seleção na extensão")
        print("💾 Documentos serão salvos no Supabase PostgreSQL")
    else:
        print("\n⚠️ Verifique os erros acima antes de usar a extensão")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 