#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se a extensão Chrome está funcionando
"""

import requests
import json
import time

def testar_servidor_flask():
    """Testa se o servidor Flask está funcionando"""
    print("🔍 TESTANDO SERVIDOR FLASK...")
    print("=" * 50)
    
    url_base = "http://localhost:5000"
    
    # Teste 1: Health check
    try:
        print("1️⃣ Testando health check...")
        response = requests.get(f"{url_base}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check OK: {data.get('message', 'OK')}")
        else:
            print(f"   ❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro no health check: {e}")
        return False
    
    # Teste 2: Listar agentes
    try:
        print("2️⃣ Testando endpoint de agentes...")
        response = requests.get(f"{url_base}/api/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print(f"   ✅ Agentes carregados: {len(agents)} agentes")
            for agent in agents:
                print(f"      📋 {agent.get('name', 'N/A')} ({agent.get('documents_count', 0)} docs)")
        else:
            print(f"   ❌ Endpoint de agentes falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro no endpoint de agentes: {e}")
        return False
    
    # Teste 3: Estatísticas
    try:
        print("3️⃣ Testando endpoint de estatísticas...")
        response = requests.get(f"{url_base}/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Estatísticas OK: {data.get('total_requests', 0)} requests")
        else:
            print(f"   ❌ Endpoint de estatísticas falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro no endpoint de estatísticas: {e}")
        return False
    
    # Teste 4: Processar conteúdo
    try:
        print("4️⃣ Testando processamento de conteúdo...")
        test_data = {
            "url": "https://example.com",
            "title": "Página de teste",
            "agent_id": "agente-geral",
            "content": "Conteúdo de teste para processamento"
        }
        
        response = requests.post(f"{url_base}/api/process", 
                               json=test_data, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Processamento OK: {data.get('message', 'OK')}")
        else:
            print(f"   ❌ Processamento falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro no processamento: {e}")
        return False
    
    print("✅ TODOS OS TESTES DO SERVIDOR PASSARAM!")
    return True

def verificar_extensao():
    """Verifica se a extensão está configurada corretamente"""
    print("\n🔧 VERIFICANDO CONFIGURAÇÃO DA EXTENSÃO...")
    print("=" * 50)
    
    # Verificar arquivos da extensão
    import os
    
    arquivos_necessarios = [
        'scraper_extension_clean/manifest.json',
        'scraper_extension_clean/popup.html',
        'scraper_extension_clean/popup.js',
        'scraper_extension_clean/background.js',
        'scraper_extension_clean/style.css',
        'scraper_extension_clean/options.html'
    ]
    
    todos_ok = True
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - NÃO ENCONTRADO")
            todos_ok = False
    
    if todos_ok:
        print("✅ TODOS OS ARQUIVOS DA EXTENSÃO ENCONTRADOS!")
    else:
        print("❌ ALGUNS ARQUIVOS DA EXTENSÃO ESTÃO FALTANDO!")
    
    return todos_ok

def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DA EXTENSÃO CHROME RAG-CONTROL")
    print("=" * 70)
    
    # Teste 1: Servidor Flask
    servidor_ok = testar_servidor_flask()
    
    # Teste 2: Arquivos da extensão
    extensao_ok = verificar_extensao()
    
    # Resultado final
    print("\n" + "=" * 70)
    print("📊 RESULTADO FINAL:")
    print("=" * 70)
    
    if servidor_ok:
        print("✅ Servidor Flask: FUNCIONANDO")
    else:
        print("❌ Servidor Flask: COM PROBLEMAS")
    
    if extensao_ok:
        print("✅ Arquivos da Extensão: OK")
    else:
        print("❌ Arquivos da Extensão: COM PROBLEMAS")
    
    if servidor_ok and extensao_ok:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("🔗 URLs para testar:")
        print("   - Servidor Flask: http://localhost:5000")
        print("   - Interface Streamlit: http://localhost:8501")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Instale a extensão no Chrome")
        print("   2. Carregue a pasta: scraper_extension_clean")
        print("   3. Teste a conexão na extensão")
        print("   4. Verifique se os agentes aparecem corretamente")
    else:
        print("\n⚠️ SISTEMA COM PROBLEMAS!")
        print("🔧 AÇÕES NECESSÁRIAS:")
        if not servidor_ok:
            print("   - Inicie o servidor Flask: python api_server_simple.py")
        if not extensao_ok:
            print("   - Verifique os arquivos da extensão")

if __name__ == "__main__":
    main() 