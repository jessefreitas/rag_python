#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 RAG Python - Inicializador Automático
========================================
Script para rodar TODOS os servidores automaticamente
"""

import os
import sys
import time
import subprocess
import threading

def run_server(script, port, name):
    """Roda um servidor em thread separada"""
    print(f"🚀 Iniciando {name} na porta {port}...")
    try:
        subprocess.run(["python", script])
    except KeyboardInterrupt:
        print(f"⏹️ {name} interrompido")
    except Exception as e:
        print(f"❌ Erro no {name}: {e}")

def main():
    print("=" * 70)
    print("🚀 RAG PYTHON v1.5.1 - INICIALIZADOR AUTOMÁTICO")
    print("=" * 70)
    print("🎯 Iniciando TODOS os servidores automaticamente...")
    print("=" * 70)
    
    # Lista de servidores para iniciar
    servers = [
        ("api_server_simple.py", 5000, "API Flask Simples"),
        ("api_server_supabase.py", 5002, "API Supabase"),
    ]
    
    # Iniciar servidores em background
    threads = []
    for script, port, name in servers:
        thread = threading.Thread(target=run_server, args=(script, port, name))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(2)  # Aguardar um pouco entre cada servidor
    
    print("\n🎯 Iniciando Streamlit (interface principal)...")
    print("📡 URLs disponíveis:")
    print("  - Streamlit: http://localhost:8501")
    print("  - API Flask: http://localhost:5000") 
    print("  - API Supabase: http://localhost:5002")
    print("=" * 70)
    print("⏹️ Pressione Ctrl+C para parar todos os servidores")
    print("=" * 70)
    
    # Streamlit como processo principal
    try:
        subprocess.run(["python", "iniciar_servidor_rag.py"])
    except KeyboardInterrupt:
        print("\n👋 Parando todos os servidores...")
        print("✅ Sistema encerrado com sucesso!")

if __name__ == "__main__":
    main() 