#!/usr/bin/env python3
"""
🔧 CORREÇÃO DOS PROVEDORES LLM
Corrige problemas com OpenRouter e DeepSeek
"""

import os
import sys
from pathlib import Path

def fix_llm_providers():
    """Aplica correções no arquivo llm_providers.py"""
    
    llm_file = Path("llm_providers.py")
    if not llm_file.exists():
        print("❌ Arquivo llm_providers.py não encontrado")
        return False
    
    # Ler conteúdo atual
    with open(llm_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aplicar correções
    corrections = [
        # Corrigir variável de ambiente do Google
        ('GOOGLE_GEMINI_API_KEY', 'GOOGLE_API_KEY'),
        
        # Corrigir nome do provedor Google
        ('name="gemini"', 'name="google"'),
        ('self.providers["gemini"]', 'self.providers["google"]'),
        ('self.active_provider = "gemini"', 'self.active_provider = "google"'),
        
        # Melhorar tratamento de modelos
        ('model=kwargs.get(\'model\', self.config.model_name)', 
         'model=kwargs.get(\'model\') or self.config.model_name'),
    ]
    
    original_content = content
    for old, new in corrections:
        content = content.replace(old, new)
    
    # Verificar se houve mudanças
    if content != original_content:
        # Fazer backup
        backup_file = llm_file.with_suffix('.py.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ Backup criado: {backup_file}")
        
        # Salvar correções
        with open(llm_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Correções aplicadas em llm_providers.py")
        return True
    else:
        print("ℹ️ Nenhuma correção necessária")
        return False

def check_api_keys():
    """Verifica status das API Keys"""
    print("\n🔑 VERIFICANDO API KEYS:")
    
    keys = {
        'OPENAI_API_KEY': 'OpenAI',
        'GOOGLE_API_KEY': 'Google Gemini',
        'OPENROUTER_API_KEY': 'OpenRouter',
        'DEEPSEEK_API_KEY': 'DeepSeek'
    }
    
    configured = 0
    for env_var, name in keys.items():
        value = os.getenv(env_var)
        if value:
            print(f"✅ {name}: Configurada")
            configured += 1
        else:
            print(f"❌ {name}: NÃO configurada")
    
    print(f"\n📊 Total: {configured}/{len(keys)} API Keys configuradas")
    return configured

def show_model_mapping():
    """Mostra mapeamento correto de modelos por provedor"""
    print("\n🤖 MAPEAMENTO CORRETO DE MODELOS:")
    
    mappings = {
        'OpenAI': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
        'Google': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],
        'OpenRouter': ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet', 'meta-llama/llama-3.1-405b-instruct'],
        'DeepSeek': ['deepseek-chat', 'deepseek-coder', 'deepseek-math']
    }
    
    for provider, models in mappings.items():
        print(f"\n🔧 {provider}:")
        for model in models[:3]:  # Mostrar primeiros 3
            print(f"   • {model}")
        if len(models) > 3:
            print(f"   • ... e mais {len(models) - 3} modelos")

def main():
    """Executa todas as correções"""
    print("🚀 CORREÇÃO DOS PROVEDORES LLM - RAG PYTHON v1.5.1")
    print("=" * 60)
    
    # 1. Aplicar correções no código
    print("1️⃣ APLICANDO CORREÇÕES NO CÓDIGO:")
    fix_llm_providers()
    
    # 2. Verificar API Keys
    configured_keys = check_api_keys()
    
    # 3. Mostrar mapeamento de modelos
    show_model_mapping()
    
    # 4. Recomendações
    print("\n" + "=" * 60)
    print("💡 RECOMENDAÇÕES:")
    
    if configured_keys < 2:
        print("⚠️ Configure pelo menos 2 API Keys para melhor funcionalidade")
        print("📝 Exemplo de configuração:")
        print("   export OPENROUTER_API_KEY='sk-or-...'")
        print("   export DEEPSEEK_API_KEY='sk-...'")
    
    print("🔄 Reinicie o servidor Streamlit para aplicar as correções")
    print("🌐 Teste os provedores na aba 'Multi-LLM > Testes'")
    
    return configured_keys >= 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 