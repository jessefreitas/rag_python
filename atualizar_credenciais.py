#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar credenciais e testar provedores
"""

import os

def atualizar_env():
    """Atualiza arquivo .env com as novas credenciais"""
    
    credenciais = {
        'OPENAI_API_KEY': 'sk-03214699d60f444c892c628e5d28f8b5',
        'GOOGLE_GEMINI_API_KEY': 'AIzaSyCuV5Jqbyp1OuMCl6lVkF3z7953KFqAuiQ',
        'GOOGLE_API_KEY': 'AIzaSyCuV5Jqbyp1OuMCl6lVkF3z7953KFqAuiQ',
        'OPENROUTER_API_KEY': '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',
        'DB_HOST': 'db.fwzztbgmzxruqmtmafhe.supabase.co',
        'DB_PORT': '5432',
        'DB_USER': 'postgres',
        'DB_PASSWORD': '30291614',
        'DB_NAME': 'postgres',
        'ENVIRONMENT': 'development',
        'LOG_LEVEL': 'INFO'
    }
    
    env_content = """# ===== RAG PYTHON - CONFIGURAÇÃO COMPLETA =====
# Credenciais atualizadas em 23/06/2025 - TODOS OS PROVEDORES

# OpenAI (configurado e funcionando)
OPENAI_API_KEY="sk-03214699d60f444c892c628e5d28f8b5"

# Google Gemini (nova configuração)
GOOGLE_GEMINI_API_KEY="AIzaSyCuV5Jqbyp1OuMCl6lVkF3z7953KFqAuiQ"
GOOGLE_API_KEY="AIzaSyCuV5Jqbyp1OuMCl6lVkF3z7953KFqAuiQ"

# OpenRouter (nova configuração)
OPENROUTER_API_KEY="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"

# DeepSeek (nova configuração - ADICIONADO!)
DEEPSEEK_API_KEY="sk-03214699d60f444c892c628e5d28f8b5"

# ===== BANCO DE DADOS SUPABASE =====
DB_HOST="db.fwzztbgmzxruqmtmafhe.supabase.co"
DB_PORT="5432"
DB_USER="postgres"
DB_PASSWORD="30291614"
DB_NAME="postgres"

# ===== CONFIGURAÇÕES OPCIONAIS =====
ENVIRONMENT=development
LOG_LEVEL=INFO

# ===== CONFIGURAÇÕES DE SEGURANÇA =====
SECRET_KEY=rag-python-secret-key-2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env atualizado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar .env: {e}")
        return False

def testar_credenciais():
    """Testa as credenciais dos provedores"""
    print("\n🧪 TESTANDO CREDENCIAIS DOS PROVEDORES:")
    print("=" * 50)
    
    # Recarregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Testar OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        models = client.models.list()
        print("✅ OpenAI: Conectado com sucesso")
    except Exception as e:
        print(f"❌ OpenAI: Erro - {e}")
    
    # Testar Google Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
        models = list(genai.list_models())
        print("✅ Google Gemini: Conectado com sucesso")
    except Exception as e:
        print(f"❌ Google Gemini: Erro - {e}")
    
    # Testar OpenRouter
    try:
        import requests
        headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        if response.status_code == 200:
            print("✅ OpenRouter: Conectado com sucesso")
        else:
            print(f"❌ OpenRouter: Erro HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ OpenRouter: Erro - {e}")
    
    # Testar DeepSeek (NOVO!)
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=os.getenv('DEEPSEEK_API_KEY')
        )
        # Teste simples de lista de modelos ou teste de chat
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ DeepSeek: Conectado com sucesso")
    except Exception as e:
        print(f"❌ DeepSeek: Erro - {e}")
    
    # Testar Supabase
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.close()
        print("✅ Supabase: Conectado com sucesso")
    except Exception as e:
        print(f"❌ Supabase: Erro - {e}")

def main():
    print("🔧 ATUALIZANDO CREDENCIAIS DO SISTEMA RAG PYTHON")
    print("=" * 60)
    
    # Atualizar arquivo .env
    if atualizar_env():
        # Testar credenciais
        testar_credenciais()
        
        print("\n🎉 CREDENCIAIS ATUALIZADAS COM SUCESSO!")
        print("🚀 Agora você pode executar:")
        print("   python implementar_proximos_passos.py --teste-modelos")
        print("   python implementar_proximos_passos.py --diagnostico")
    
if __name__ == "__main__":
    main() 