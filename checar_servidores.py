#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar status de todos os servidores RAG
"""

import requests
import time
from datetime import datetime

def checar_servidor(nome, url, timeout=3):
    """Verifica se um servidor está funcionando"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return f"✅ {nome}: FUNCIONANDO (Status: {response.status_code})"
        else:
            return f"⚠️ {nome}: RESPONDENDO mas com erro (Status: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return f"❌ {nome}: NÃO CONECTA (Servidor offline)"
    except requests.exceptions.Timeout:
        return f"⏰ {nome}: TIMEOUT (Servidor lento)"
    except Exception as e:
        return f"❌ {nome}: ERRO ({str(e)})"

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO COMPLETA DOS SERVIDORES RAG PYTHON")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Lista de servidores para verificar
    servidores = [
        {
            "nome": "Streamlit Principal (8501)",
            "url": "http://localhost:8501"
        },
        {
            "nome": "API Flask Simples (5000)",
            "url": "http://localhost:5000/api/health"
        },
        {
            "nome": "API Flask Completa (5000)",
            "url": "http://localhost:5000/api"
        },
        {
            "nome": "API Supabase (5002)",
            "url": "http://localhost:5002/api/health"
        },
        {
            "nome": "Streamlit Multi-LLM (8503)",
            "url": "http://localhost:8503"
        },
        {
            "nome": "Streamlit Integrado (8505)",
            "url": "http://localhost:8505"
        }
    ]
    
    # Verificar cada servidor
    resultados = []
    for servidor in servidores:
        print(f"🔍 Verificando {servidor['nome']}...")
        resultado = checar_servidor(servidor['nome'], servidor['url'])
        resultados.append(resultado)
        print(f"   {resultado}")
        time.sleep(0.5)  # Pequena pausa entre verificações
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL:")
    print("=" * 60)
    
    funcionando = sum(1 for r in resultados if "✅" in r)
    com_problema = sum(1 for r in resultados if "⚠️" in r)
    offline = sum(1 for r in resultados if "❌" in r or "⏰" in r)
    
    print(f"✅ Funcionando: {funcionando}")
    print(f"⚠️ Com problemas: {com_problema}")
    print(f"❌ Offline: {offline}")
    print(f"📊 Total verificado: {len(servidores)}")
    
    # Teste específico da extensão Chrome
    print("\n" + "=" * 60)
    print("🔧 TESTE ESPECÍFICO PARA EXTENSÃO CHROME:")
    print("=" * 60)
    
    try:
        # Testar endpoint de agentes
        response = requests.get("http://localhost:5000/api/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print(f"✅ Endpoint /api/agents: {len(agents)} agentes disponíveis")
            for agent in agents:
                print(f"   📋 {agent.get('name', 'N/A')} ({agent.get('documents_count', 0)} docs)")
        else:
            print(f"❌ Endpoint /api/agents: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar agentes: {e}")
    
    # Instruções finais
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASSOS:")
    print("=" * 60)
    
    if funcionando >= 2:
        print("✅ Sistema parcialmente funcional!")
        print("🔗 URLs disponíveis:")
        for resultado in resultados:
            if "✅" in resultado:
                nome = resultado.split(":")[0].replace("✅ ", "")
                if "8501" in nome:
                    print("   📱 Interface Principal: http://localhost:8501")
                elif "5000" in nome:
                    print("   🔌 API para Extensão: http://localhost:5000")
    else:
        print("⚠️ Sistema com problemas!")
        print("🔧 Ações recomendadas:")
        print("   1. Iniciar Streamlit: streamlit run app_completo_unificado.py --server.port 8501")
        print("   2. Iniciar API Flask: python api_server_simple.py")
        print("   3. Verificar portas em uso: netstat -an | findstr :8501")

if __name__ == "__main__":
    main() 