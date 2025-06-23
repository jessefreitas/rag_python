#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção do Sistema de Roteamento de Modelos
Evita envio de modelos incompatíveis para APIs erradas
"""

import os
import sys

def fix_model_routing():
    """Corrige o roteamento de modelos no sistema"""
    
    print("🔧 CORREÇÃO DO ROTEAMENTO DE MODELOS")
    print("=" * 40)
    
    # 1. Verificar provedores configurados
    configured_providers = []
    
    if os.getenv('OPENAI_API_KEY'):
        configured_providers.append('openai')
        print("✅ OpenAI: Configurado")
    else:
        print("❌ OpenAI: Não configurado")
    
    if os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_GEMINI_API_KEY'):
        configured_providers.append('google')
        print("✅ Google: Configurado")
    else:
        print("❌ Google: Não configurado")
    
    if os.getenv('OPENROUTER_API_KEY'):
        configured_providers.append('openrouter')
        print("✅ OpenRouter: Configurado")
    else:
        print("❌ OpenRouter: Não configurado")
    
    if os.getenv('DEEPSEEK_API_KEY'):
        configured_providers.append('deepseek')
        print("✅ DeepSeek: Configurado")
    else:
        print("❌ DeepSeek: Não configurado")
    
    print(f"\n📊 Provedores configurados: {len(configured_providers)}/4")
    
    # 2. Definir modelos seguros por provedor
    safe_models = {
        'openai': [
            'gpt-4o',
            'gpt-4o-mini', 
            'gpt-4-turbo',
            'gpt-4',
            'gpt-3.5-turbo'
        ],
        'google': [
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-pro'
        ],
        'openrouter': [
            'openai/gpt-4o',
            'anthropic/claude-3.5-sonnet',
            'meta-llama/llama-3.1-405b-instruct'
        ],
        'deepseek': [
            'deepseek-chat',
            'deepseek-coder'
        ]
    }
    
    # 3. Mostrar modelos disponíveis
    print(f"\n🎯 MODELOS SEGUROS DISPONÍVEIS:")
    print("-" * 30)
    
    total_models = 0
    for provider in configured_providers:
        if provider in safe_models:
            models = safe_models[provider]
            total_models += len(models)
            print(f"\n🔹 {provider.upper()}:")
            for model in models:
                print(f"   ✅ {model}")
    
    print(f"\n📈 Total de modelos disponíveis: {total_models}")
    
    # 4. Recomendações
    print(f"\n💡 RECOMENDAÇÕES:")
    print("-" * 20)
    
    if 'openai' in configured_providers:
        print("✅ Use modelos OpenAI para máxima compatibilidade")
        print("   Recomendado: gpt-4o-mini (rápido e barato)")
    
    if len(configured_providers) == 1 and 'openai' in configured_providers:
        print("⚠️  Apenas OpenAI configurado")
        print("   Configure outros provedores para mais opções")
    
    if len(configured_providers) == 0:
        print("❌ Nenhum provedor configurado!")
        print("   Configure pelo menos OPENAI_API_KEY")
    
    return configured_providers, safe_models

def create_model_filter_config():
    """Cria arquivo de configuração para filtro de modelos"""
    
    configured_providers, safe_models = fix_model_routing()
    
    # Criar configuração filtrada
    filtered_config = {}
    for provider in configured_providers:
        if provider in safe_models:
            filtered_config[provider] = safe_models[provider]
    
    config_content = f'''# Configuração Automática de Modelos Seguros
# Gerado em: {os.popen("date /t").read().strip()} {os.popen("time /t").read().strip()}

SAFE_MODELS = {filtered_config}

CONFIGURED_PROVIDERS = {configured_providers}

def get_safe_models():
    """Retorna apenas modelos de provedores configurados"""
    return SAFE_MODELS

def is_model_safe(provider, model):
    """Verifica se um modelo é seguro para o provedor"""
    return provider in SAFE_MODELS and model in SAFE_MODELS[provider]
'''
    
    with open('models_safe_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n✅ Arquivo 'models_safe_config.py' criado")
    print("   Use este arquivo para evitar erros de modelo")
    
    return True

if __name__ == "__main__":
    print("🚀 SISTEMA DE CORREÇÃO DE MODELOS")
    print("=================================")
    
    try:
        create_model_filter_config()
        print("\n🎉 Correção concluída com sucesso!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Reinicie o sistema Streamlit")
        print("2. Use apenas modelos da lista segura")
        print("3. Configure mais provedores se necessário")
        
    except Exception as e:
        print(f"\n❌ Erro na correção: {e}")
        sys.exit(1) 