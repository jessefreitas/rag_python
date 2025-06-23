#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 RAG Python - Inicializador Rápido
====================================
Script para rodar qualquer servidor do sistema
"""

import os
import sys
import time
import subprocess

def main():
    print("=" * 70)
    print("🚀 RAG PYTHON v1.5.1 - INICIALIZADOR RÁPIDO")
    print("=" * 70)
    
    print("🎯 ESCOLHA O SERVIDOR:")
    print("1. 🎯 STREAMLIT - Interface principal (porta 8501)")
    print("2. 🔌 API FLASK SIMPLES - API para extensão (porta 5000)")
    print("3. 🗄️ API SUPABASE - API com Supabase (porta 5002)")
    print("4. 🚀 INICIALIZADOR ROBUSTO - Script com verificações")
    print("=" * 70)
    
    choice = input("Digite sua escolha (1-4): ").strip()
    
    if choice == "1":
        print("\n🎯 Iniciando Streamlit...")
        print("📡 URL: http://localhost:8501")
        print("⏹️ Pressione Ctrl+C para parar")
        subprocess.run(["streamlit", "run", "app_completo_unificado.py", "--server.port", "8501"])
        
    elif choice == "2":
        print("\n🔌 Iniciando API Flask Simples...")
        print("📡 URL: http://localhost:5000")
        print("⏹️ Pressione Ctrl+C para parar")
        subprocess.run(["python", "api_server_simple.py"])
        
    elif choice == "3":
        print("\n🗄️ Iniciando API Supabase...")
        print("📡 URL: http://localhost:5002")
        print("⏹️ Pressione Ctrl+C para parar")
        subprocess.run(["python", "api_server_supabase.py"])
        
    elif choice == "4":
        print("\n🚀 Iniciando com script robusto...")
        print("📡 URL: http://localhost:8501")
        print("⏹️ Pressione Ctrl+C para parar")
        subprocess.run(["python", "iniciar_servidor_rag.py"])
        
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    main() 