#!/usr/bin/env python3
"""
Script final para criar GitHub Release v1.5.1 automaticamente
"""

import requests
import json
import os
import base64
from pathlib import Path

# Configurações
OWNER = "jessefreitas"
REPO = "rag_python"
TAG_NAME = "v1.5.1-release"
RELEASE_NAME = "🚀 RAG Python v1.5.1 - Production Release"

def read_release_notes():
    """Ler as release notes do arquivo"""
    try:
        with open("release-assets/RELEASE_NOTES_v1.5.1.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Erro ao ler release notes: {e}")
        return None

def create_github_release_simple():
    """Criar GitHub Release usando requests simples"""
    
    print("🎯 RAG Python v1.5.1 - GitHub Release Creator")
    print("=" * 50)
    
    # Ler release notes
    release_body = read_release_notes()
    if not release_body:
        print("❌ Não foi possível ler as release notes")
        return False
    
    # URL da API
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"
    
    # Headers básicos
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-RAG-Release-Creator",
        "Content-Type": "application/json"
    }
    
    # Dados da release
    data = {
        "tag_name": TAG_NAME,
        "target_commitish": "main",
        "name": RELEASE_NAME,
        "body": release_body,
        "draft": False,
        "prerelease": False
    }
    
    try:
        print("🚀 Criando GitHub Release...")
        print(f"📋 Tag: {TAG_NAME}")
        print(f"📋 Nome: {RELEASE_NAME}")
        
        # Tentar criar sem autenticação primeiro (repositório público)
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            release_data = response.json()
            print("🎉 Release criada com sucesso!")
            print(f"🔗 URL: {release_data['html_url']}")
            print(f"📦 Download: {release_data['zipball_url']}")
            return release_data
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
            # Se falhar, tentar com método alternativo
            return create_release_alternative()
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return create_release_alternative()

def create_release_alternative():
    """Método alternativo - criar release via GitHub CLI se disponível"""
    
    print("\n🔄 Tentando método alternativo...")
    
    # Verificar se gh CLI está disponível
    import subprocess
    
    try:
        # Testar gh CLI
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GitHub CLI encontrado!")
            return create_with_gh_cli()
        else:
            print("❌ GitHub CLI não encontrado")
            return show_manual_instructions()
    except FileNotFoundError:
        print("❌ GitHub CLI não instalado")
        return show_manual_instructions()

def create_with_gh_cli():
    """Criar release usando GitHub CLI"""
    
    import subprocess
    
    try:
        print("🚀 Criando release com GitHub CLI...")
        
        cmd = [
            "gh", "release", "create", TAG_NAME,
            "--title", RELEASE_NAME,
            "--notes-file", "release-assets/RELEASE_NOTES_v1.5.1.md",
            "--latest"
        ]
        
        # Adicionar assets se existirem
        assets = [
            "release-assets/QUICK_START_v1.5.1.md",
            "release-assets/requirements.txt",
            "release-assets/pytest.ini",
            "release-assets/test_results_v1.5.0_final.json"
        ]
        
        for asset in assets:
            if os.path.exists(asset):
                cmd.extend([asset])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🎉 Release criada com sucesso via GitHub CLI!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro no GitHub CLI: {result.stderr}")
            return show_manual_instructions()
            
    except Exception as e:
        print(f"❌ Erro no GitHub CLI: {e}")
        return show_manual_instructions()

def show_manual_instructions():
    """Mostrar instruções manuais"""
    
    print("\n📋 INSTRUÇÕES PARA CRIAÇÃO MANUAL:")
    print("=" * 50)
    print(f"1. 🔗 Acesse: https://github.com/{OWNER}/{REPO}/releases/new")
    print(f"2. 🏷️  Tag: {TAG_NAME}")
    print(f"3. 📝 Title: {RELEASE_NAME}")
    print("4. 📄 Description: Cole o conteúdo de release-assets/RELEASE_NOTES_v1.5.1.md")
    print("5. 📎 Assets: Anexe os arquivos:")
    
    assets = [
        "release-assets/QUICK_START_v1.5.1.md",
        "release-assets/requirements.txt", 
        "release-assets/pytest.ini",
        "release-assets/test_results_v1.5.0_final.json"
    ]
    
    for asset in assets:
        if os.path.exists(asset):
            print(f"   ✅ {asset}")
        else:
            print(f"   ❌ {asset} (não encontrado)")
    
    print("6. ✅ Marque 'Set as the latest release'")
    print("7. 🚀 Clique 'Publish release'")
    
    return False

def verify_release_created():
    """Verificar se a release foi criada"""
    
    print("\n🔍 Verificando releases...")
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"
    
    try:
        response = requests.get(url)
        releases = response.json()
        
        if len(releases) > 0:
            print(f"✅ {len(releases)} release(s) encontrada(s):")
            for rel in releases:
                print(f"   📦 {rel['name']} ({rel['tag_name']})")
                print(f"   🔗 {rel['html_url']}")
            return True
        else:
            print("❌ Nenhuma release encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    
    # Verificar se já existe release
    if verify_release_created():
        print("✅ Release já existe!")
        return
    
    # Tentar criar release
    result = create_github_release_simple()
    
    if result:
        print("\n🎊 SUCESSO! Release v1.5.1 publicada!")
        verify_release_created()
    else:
        print("\n💡 Siga as instruções manuais acima")

if __name__ == "__main__":
    main() 