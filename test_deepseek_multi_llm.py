#!/usr/bin/env python3
"""
Script de teste para o sistema Multi-LLM expandido com DeepSeek
Teste funcionalidades: DeepSeek, comparação multi-LLM, recomendação de modelos
"""

import os
import sys
import json
from dotenv import load_dotenv
from typing import Dict, Any, List

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_providers import LLMProviderManager

def test_deepseek_connection():
    """Testa conexão com DeepSeek"""
    print("🔍 Testando conexão com DeepSeek...")
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("⚠️  DEEPSEEK_API_KEY não configurada")
        return False
    
    manager = LLMProviderManager()
    
    if "deepseek" not in manager.providers:
        print("❌ Provedor DeepSeek não carregado")
        return False
    
    print("✅ DeepSeek configurado com sucesso!")
    return True

def test_multi_llm_comparison():
    """Testa comparação entre múltiplos LLMs"""
    print("\n🔄 Testando comparação Multi-LLM...")
    
    manager = LLMProviderManager()
    available_providers = manager.list_available_providers()
    
    if not available_providers:
        print("❌ Nenhum provedor configurado")
        return
    
    print(f"📋 Provedores disponíveis: {available_providers}")
    
    # Pergunta simples para testar
    messages = [
        {"role": "user", "content": "Explique o que é inteligência artificial em uma frase."}
    ]
    
    results = manager.compare_multi_llm(messages, max_tokens=100)
    
    print("\n📊 Resultados da comparação:")
    for provider, result in results.items():
        if result["success"]:
            print(f"\n🤖 {provider.upper()} ({result['model']}):")
            print(f"   Resposta: {result['response'][:100]}...")
            print(f"   Tempo: {result['duration']}s")
        else:
            print(f"\n❌ {provider.upper()}: {result.get('error', 'Erro desconhecido')}")

def test_provider_recommendations():
    """Testa sistema de recomendação de provedores"""
    print("\n🎯 Testando recomendações de provedores...")
    
    manager = LLMProviderManager()
    
    tasks = ["general", "coding", "creative", "analysis", "legal"]
    
    for task in tasks:
        best_provider = manager.get_best_provider_for_task(task)
        print(f"📌 Melhor para {task}: {best_provider}")

def test_provider_info():
    """Testa informações dos provedores"""
    print("\n📋 Informações dos provedores configurados:")
    
    manager = LLMProviderManager()
    info = manager.get_provider_info()
    
    print(json.dumps(info, indent=2, ensure_ascii=False))

def test_model_listing():
    """Testa listagem de modelos disponíveis"""
    print("\n📚 Testando listagem de modelos...")
    
    manager = LLMProviderManager()
    
    for provider_name in manager.list_available_providers():
        try:
            models = manager.get_provider_models(provider_name)
            print(f"\n🔧 {provider_name.upper()} - Modelos:")
            for model in models[:5]:  # Mostra apenas os primeiros 5
                print(f"   • {model}")
            if len(models) > 5:
                print(f"   ... e mais {len(models) - 5} modelos")
        except Exception as e:
            print(f"❌ Erro ao listar modelos para {provider_name}: {e}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema Multi-LLM expandido")
    print("=" * 60)
    
    # Teste 1: Conexão DeepSeek
    test_deepseek_connection()
    
    # Teste 2: Informações dos provedores
    test_provider_info()
    
    # Teste 3: Recomendações
    test_provider_recommendations()
    
    # Teste 4: Listagem de modelos
    test_model_listing()
    
    # Teste 5: Comparação multi-LLM (opcional, requer APIs configuradas)
    response = input("\n🤔 Executar teste de comparação multi-LLM? (consome tokens) [y/N]: ")
    if response.lower() in ['y', 'yes', 's', 'sim']:
        test_multi_llm_comparison()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main() 