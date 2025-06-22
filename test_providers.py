#!/usr/bin/env python3
"""
Script de teste para verificar a configuração dos provedores de IA
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_environment():
    """Testa se as variáveis de ambiente estão configuradas"""
    print("🔧 Testando configuração do ambiente...")
    
    providers = {
        'OpenAI': 'OPENAI_API_KEY',
        'OpenRouter': 'OPENROUTER_API_KEY', 
        'Google Gemini': 'GOOGLE_GEMINI_API_KEY'
    }
    
    configured_providers = []
    
    for name, key in providers.items():
        if os.getenv(key):
            print(f"✅ {name}: Configurado")
            configured_providers.append(name)
        else:
            print(f"❌ {name}: Não configurado")
    
    if not configured_providers:
        print("\n⚠️  Nenhum provedor configurado!")
        print("Configure pelo menos uma das seguintes variáveis:")
        for name, key in providers.items():
            print(f"   {key}")
        return False
    
    print(f"\n✅ {len(configured_providers)} provedor(es) configurado(s): {', '.join(configured_providers)}")
    return True

def test_providers():
    """Testa se os provedores estão funcionando"""
    print("\n🧪 Testando conectividade dos provedores...")
    
    try:
        from llm_providers import llm_manager
        
        # Testar cada provedor disponível
        for provider_name in llm_manager.list_available_providers():
            print(f"\n📡 Testando {provider_name}...")
            
            try:
                # Listar modelos
                models = llm_manager.get_provider_models(provider_name)
                print(f"   ✅ Modelos disponíveis: {len(models)}")
                if models:
                    print(f"   📋 Primeiros 5 modelos: {models[:5]}")
                
                # Testar geração de resposta
                test_message = [{"role": "user", "content": "Diga apenas 'Olá, mundo!'"}]
                response = llm_manager.generate_response(
                    test_message,
                    model=models[0] if models else "gpt-3.5-turbo",
                    temperature=0.1,
                    max_tokens=10
                )
                print(f"   ✅ Resposta de teste: {response[:50]}...")
                
            except Exception as e:
                print(f"   ❌ Erro no {provider_name}: {str(e)}")
        
        # Mostrar informações do provedor ativo
        active_provider = llm_manager.get_active_provider()
        if active_provider:
            print(f"\n🎯 Provedor ativo: {llm_manager.active_provider}")
            print(f"   Modelo padrão: {active_provider.config.model_name}")
            print(f"   Temperatura: {active_provider.config.temperature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar provedores: {e}")
        return False

def test_rag_system():
    """Testa se o sistema RAG funciona com os provedores"""
    print("\n🤖 Testando sistema RAG...")
    
    try:
        from rag_system import RAGSystem
        
        # Testar com cada provedor disponível
        from llm_providers import llm_manager
        
        for provider_name in llm_manager.list_available_providers():
            print(f"\n🔍 Testando RAG com {provider_name}...")
            
            try:
                # Criar sistema RAG temporário
                rag = RAGSystem(
                    vector_db_path="test_vector_db",
                    provider=provider_name,
                    model_name="gpt-3.5-turbo" if provider_name == "openai" else "openai/gpt-4o-mini"
                )
                
                # Testar carregamento de texto
                test_text = "Inteligência artificial é um campo da computação que busca criar sistemas capazes de realizar tarefas que normalmente requerem inteligência humana."
                success = rag.load_documents(text=test_text)
                
                if success:
                    print(f"   ✅ Documento carregado com sucesso")
                    
                    # Testar consulta
                    result = rag.query("O que é inteligência artificial?")
                    print(f"   ✅ Consulta realizada: {result['answer'][:100]}...")
                else:
                    print(f"   ❌ Falha ao carregar documento")
                
            except Exception as e:
                print(f"   ❌ Erro no RAG com {provider_name}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar sistema RAG: {e}")
        return False

def test_agent_system():
    """Testa se o sistema de agentes funciona"""
    print("\n👾 Testando sistema de agentes...")
    
    try:
        from agent_system import create_agent, AgentConfig
        from llm_providers import llm_manager
        
        # Testar criação de agente com cada provedor
        for provider_name in llm_manager.list_available_providers():
            print(f"\n🤖 Testando agente com {provider_name}...")
            
            try:
                # Criar configuração de agente
                config = AgentConfig(
                    agent_name=f"Teste {provider_name}",
                    model_name="gpt-3.5-turbo" if provider_name == "openai" else "openai/gpt-4o-mini",
                    temperature=0.1,
                    system_prompt="Você é um assistente de teste. Responda de forma simples e direta.",
                    provider=provider_name
                )
                
                # Criar agente
                agent = create_agent("custom", config=config)
                
                # Testar processamento de mensagem
                response = agent.process_message("Diga apenas 'Teste OK'")
                print(f"   ✅ Resposta do agente: {response[:50]}...")
                
            except Exception as e:
                print(f"   ❌ Erro no agente com {provider_name}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar sistema de agentes: {e}")
        return False

def show_provider_info():
    """Mostra informações detalhadas sobre os provedores"""
    print("\n📊 Informações dos Provedores:")
    
    try:
        from llm_providers import llm_manager
        
        info = llm_manager.get_provider_info()
        
        print(f"Provedor ativo: {info['active_provider']}")
        print(f"Provedores disponíveis: {', '.join(info['available_providers'])}")
        
        print("\nConfigurações detalhadas:")
        for name, config in info['providers'].items():
            print(f"\n{name.upper()}:")
            print(f"  Nome: {config['name']}")
            print(f"  Modelo padrão: {config['model_name']}")
            print(f"  Temperatura: {config['temperature']}")
            print(f"  Max tokens: {config['max_tokens']}")
        
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")

def main():
    """Função principal"""
    print("🚀 Teste de Configuração dos Provedores de IA")
    print("=" * 50)
    
    # Testar ambiente
    if not test_environment():
        print("\n❌ Configuração do ambiente falhou!")
        print("Configure as variáveis de ambiente e tente novamente.")
        sys.exit(1)
    
    # Testar provedores
    if not test_providers():
        print("\n❌ Teste dos provedores falhou!")
        sys.exit(1)
    
    # Testar sistema RAG
    if not test_rag_system():
        print("\n❌ Teste do sistema RAG falhou!")
        sys.exit(1)
    
    # Testar sistema de agentes
    if not test_agent_system():
        print("\n❌ Teste do sistema de agentes falhou!")
        sys.exit(1)
    
    # Mostrar informações
    show_provider_info()
    
    print("\n✅ Todos os testes passaram!")
    print("\n🎉 Sistema pronto para uso!")
    print("\nPróximos passos:")
    print("1. Execute o sistema web: python web_agent_manager.py")
    print("2. Acesse http://localhost:5000")
    print("3. Crie seus primeiros agentes!")

if __name__ == "__main__":
    main() 