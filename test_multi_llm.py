#!/usr/bin/env python3
"""
Script de teste para demonstrar a funcionalidade de comparação multi-LLM
"""

import requests
import json
import time
from typing import Dict, List, Any

# Configuração
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/v1"

def test_multi_llm_comparison():
    """Testa a funcionalidade de comparação multi-LLM"""
    
    print("🤖 Teste de Comparação Multi-LLM")
    print("=" * 50)
    
    # 1. Listar agentes disponíveis
    print("\n1. Listando agentes disponíveis...")
    try:
        response = requests.get(f"{API_BASE}/agents")
        agents = response.json()
        
        if not agents:
            print("❌ Nenhum agente encontrado. Crie um agente primeiro.")
            return
        
        agent = agents[0]  # Usar o primeiro agente
        agent_id = agent['id']
        print(f"✅ Usando agente: {agent['name']} (ID: {agent_id})")
        
    except Exception as e:
        print(f"❌ Erro ao listar agentes: {e}")
        return
    
    # 2. Verificar provedores disponíveis
    print("\n2. Verificando provedores disponíveis...")
    try:
        response = requests.get(f"{API_BASE}/providers")
        providers = response.json()
        print(f"✅ Provedores disponíveis: {list(providers.keys())}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar provedores: {e}")
        return
    
    # 3. Testar consulta normal (single LLM)
    print("\n3. Testando consulta normal (single LLM)...")
    question = "Explique o que é inteligência artificial em 2 parágrafos."
    
    try:
        response = requests.post(f"{API_BASE}/agents/{agent_id}/query", 
                               json={"question": question, "use_multi_llm": False})
        result = response.json()
        
        if "error" in result:
            print(f"❌ Erro na consulta normal: {result['error']}")
        else:
            print(f"✅ Resposta normal ({result['model_name']}):")
            print(f"   {result['response'][:200]}...")
            
    except Exception as e:
        print(f"❌ Erro na consulta normal: {e}")
    
    # 4. Testar consulta multi-LLM
    print("\n4. Testando consulta multi-LLM...")
    
    try:
        response = requests.post(f"{API_BASE}/agents/{agent_id}/query", 
                               json={
                                   "question": question,
                                   "use_multi_llm": True,
                                   "providers": ["openai", "openrouter"]
                               })
        result = response.json()
        
        if "error" in result:
            print(f"❌ Erro na consulta multi-LLM: {result['error']}")
        else:
            print(f"✅ Respostas multi-LLM:")
            print(f"   Provedores usados: {result['providers_used']}")
            
            for provider, response_data in result['responses'].items():
                print(f"\n   📝 {provider.upper()} ({response_data['model']}):")
                print(f"   {response_data['response'][:150]}...")
            
            # Mostrar estatísticas de comparação
            if result.get('comparison'):
                comparison = result['comparison']
                print(f"\n   📊 Estatísticas de comparação:")
                print(f"   - Respostas únicas: {comparison['unique_responses']}")
                print(f"   - Tamanhos: {comparison['response_lengths']}")
                
    except Exception as e:
        print(f"❌ Erro na consulta multi-LLM: {e}")
    
    # 5. Testar diferentes tipos de perguntas
    print("\n5. Testando diferentes tipos de perguntas...")
    
    test_questions = [
        "Qual é a diferença entre machine learning e deep learning?",
        "Explique o conceito de overfitting em machine learning.",
        "Como funciona o algoritmo de gradient descent?",
        "Quais são as principais aplicações da IA na medicina?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n   Pergunta {i}: {question}")
        
        try:
            response = requests.post(f"{API_BASE}/agents/{agent_id}/query", 
                                   json={
                                       "question": question,
                                       "use_multi_llm": True,
                                       "providers": ["openai", "openrouter"]
                                   })
            result = response.json()
            
            if "error" not in result:
                print(f"   ✅ Respostas obtidas de {len(result['responses'])} provedores")
                
                # Comparar tamanhos das respostas
                lengths = result['comparison']['response_lengths']
                print(f"   📏 Tamanhos: {lengths}")
                
                # Identificar a resposta mais longa e mais curta
                longest_provider = max(lengths, key=lengths.get)
                shortest_provider = min(lengths, key=lengths.get)
                print(f"   📈 Mais longa: {longest_provider} ({lengths[longest_provider]} chars)")
                print(f"   📉 Mais curta: {shortest_provider} ({lengths[shortest_provider]} chars)")
                
            else:
                print(f"   ❌ Erro: {result['error']}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Pausa entre perguntas para não sobrecarregar
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print("✅ Teste de comparação multi-LLM concluído!")

def test_provider_specific_queries():
    """Testa consultas específicas por provedor"""
    
    print("\n🔧 Teste de Consultas Específicas por Provedor")
    print("=" * 50)
    
    # Listar agentes
    try:
        response = requests.get(f"{API_BASE}/agents")
        agents = response[0] if response else None
        
        if not agents:
            print("❌ Nenhum agente encontrado.")
            return
            
        agent_id = agents[0]['id']
        
    except Exception as e:
        print(f"❌ Erro ao obter agentes: {e}")
        return
    
    # Testar cada provedor individualmente
    providers = ["openai", "openrouter"]
    question = "Explique o que é um transformer em deep learning."
    
    for provider in providers:
        print(f"\n📡 Testando provedor: {provider.upper()}")
        
        try:
            response = requests.post(f"{API_BASE}/agents/{agent_id}/query", 
                                   json={
                                       "question": question,
                                       "use_multi_llm": True,
                                       "providers": [provider]
                                   })
            result = response.json()
            
            if "error" not in result and provider in result['responses']:
                response_data = result['responses'][provider]
                print(f"   ✅ Modelo: {response_data['model']}")
                print(f"   📝 Resposta: {response_data['response'][:200]}...")
                print(f"   📏 Tamanho: {len(response_data['response'])} caracteres")
            else:
                print(f"   ❌ Erro ou provedor não disponível")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def test_feedback_system():
    """Testa o sistema de feedback"""
    
    print("\n👍 Teste do Sistema de Feedback")
    print("=" * 50)
    
    # Listar agentes
    try:
        response = requests.get(f"{API_BASE}/agents")
        agents = response.json()
        
        if not agents:
            print("❌ Nenhum agente encontrado.")
            return
            
        agent_id = agents[0]['id']
        
    except Exception as e:
        print(f"❌ Erro ao obter agentes: {e}")
        return
    
    # Fazer uma consulta
    question = "O que é machine learning?"
    
    try:
        response = requests.post(f"{API_BASE}/agents/{agent_id}/query", 
                               json={"question": question, "use_multi_llm": False})
        result = response.json()
        
        if "error" not in result:
            agent_response = result['response']
            print(f"✅ Pergunta: {question}")
            print(f"📝 Resposta: {agent_response[:100]}...")
            
            # Enviar feedback positivo
            feedback_response = requests.post(f"{API_BASE}/agents/{agent_id}/feedback", 
                                            json={
                                                "user_input": question,
                                                "agent_response": agent_response,
                                                "rating": "good"
                                            })
            
            if feedback_response.json().get('success'):
                print("✅ Feedback positivo enviado com sucesso!")
            else:
                print("❌ Erro ao enviar feedback positivo")
                
        else:
            print(f"❌ Erro na consulta: {result['error']}")
            
    except Exception as e:
        print(f"❌ Erro no teste de feedback: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando testes do sistema multi-LLM")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ Servidor está rodando")
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        print("   Execute: python web_agent_manager.py")
        return
    
    # Executar testes
    test_multi_llm_comparison()
    test_provider_specific_queries()
    test_feedback_system()
    
    print("\n" + "=" * 60)
    print("🎉 Todos os testes concluídos!")
    print("\n💡 Dicas:")
    print("   - Use a interface web para testar interativamente")
    print("   - Compare respostas de diferentes provedores")
    print("   - Avalie as respostas com o sistema de feedback")
    print("   - Monitore as estatísticas no dashboard")

if __name__ == "__main__":
    main() 