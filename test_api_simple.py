#!/usr/bin/env python3
"""
Teste Simples da API REST - RAG Python v1.4.0
"""

import requests
import time
import json
from datetime import datetime

def test_simple_api():
    """Teste básico da API"""
    print("🧪 Teste Simples da API REST v1.4.0")
    print("=" * 50)
    
    base_url = "http://192.168.8.4:5000"
    
    try:
        # Teste básico de conexão
        print("🔍 Testando conexão...")
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API está funcionando!")
            health_data = response.json()
            print(f"📊 Status: {health_data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ API retornou status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API")
        print("💡 Inicie a API com: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_api()
    if success:
        print("\n🎉 Teste passou! API está funcionando.")
    else:
        print("\n❌ Teste falhou. Verifique a API.") 