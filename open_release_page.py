#!/usr/bin/env python3
"""
Script para abrir página de criação de release e mostrar dados para colar
"""

import webbrowser
import os
import time

def open_release_page():
    """Abrir página de criação de release no navegador"""
    
    url = "https://github.com/jessefreitas/rag_python/releases/new"
    
    print("🚀 RAG Python v1.5.1 - Criação Automática de Release")
    print("=" * 60)
    
    print("🌐 Abrindo página de criação de release...")
    webbrowser.open(url)
    
    time.sleep(2)
    
    print("\n📋 DADOS PARA PREENCHIMENTO:")
    print("=" * 40)
    
    print("🏷️  TAG:")
    print("v1.5.1-release")
    
    print("\n📝 TÍTULO:")
    print("🚀 RAG Python v1.5.1 - Production Release")
    
    print("\n📄 DESCRIÇÃO:")
    print("(Cole o conteúdo abaixo)")
    print("-" * 40)
    
    # Ler e mostrar release notes
    try:
        with open("release-assets/RELEASE_NOTES_v1.5.1.md", "r", encoding="utf-8") as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"❌ Erro ao ler release notes: {e}")
    
    print("\n📎 ASSETS PARA UPLOAD:")
    print("=" * 30)
    
    assets = [
        "release-assets/QUICK_START_v1.5.1.md",
        "release-assets/requirements.txt",
        "release-assets/pytest.ini", 
        "release-assets/test_results_v1.5.0_final.json"
    ]
    
    for asset in assets:
        if os.path.exists(asset):
            print(f"✅ {asset}")
        else:
            print(f"❌ {asset} (não encontrado)")
    
    print("\n⚙️  CONFIGURAÇÕES:")
    print("✅ Marque 'Set as the latest release'")
    print("❌ NÃO marque 'This is a pre-release'")
    
    print("\n🎉 PRONTO! Clique 'Publish release' quando terminar!")

if __name__ == "__main__":
    open_release_page() 