#!/usr/bin/env python3
"""
Script definitivo para criar GitHub Release v1.5.1 com upload de assets
"""

import requests
import json
import os
import time

# Configurações
OWNER = "jessefreitas"
REPO = "rag_python"
TAG_NAME = "v1.5.1-release"
RELEASE_NAME = "🚀 RAG Python v1.5.1 - Production Release"

def create_release_complete():
    """Criar release completa com todos os assets"""
    
    print("🎯 RAG Python v1.5.1 - Release Creator & Uploader")
    print("=" * 60)
    
    # 1. Verificar se release já existe
    print("🔍 Verificando releases existentes...")
    releases_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"
    
    try:
        response = requests.get(releases_url)
        existing_releases = response.json()
        
        for release in existing_releases:
            if release['tag_name'] == TAG_NAME:
                print(f"✅ Release {TAG_NAME} já existe!")
                print(f"🔗 URL: {release['html_url']}")
                return True
                
        print(f"📋 Nenhuma release encontrada para {TAG_NAME}")
        
    except Exception as e:
        print(f"⚠️  Erro ao verificar releases: {e}")
    
    # 2. Ler release notes
    print("📄 Carregando release notes...")
    try:
        with open("release-assets/RELEASE_NOTES_v1.5.1.md", "r", encoding="utf-8") as f:
            release_body = f.read()
        print("✅ Release notes carregadas")
    except Exception as e:
        print(f"❌ Erro ao ler release notes: {e}")
        return False
    
    # 3. Criar release
    print("🚀 Criando release...")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-RAG-Release-Creator"
    }
    
    data = {
        "tag_name": TAG_NAME,
        "target_commitish": "main", 
        "name": RELEASE_NAME,
        "body": release_body,
        "draft": False,
        "prerelease": False
    }
    
    try:
        response = requests.post(releases_url, headers=headers, json=data)
        
        if response.status_code == 201:
            release_data = response.json()
            print("🎉 Release criada com sucesso!")
            print(f"🔗 URL: {release_data['html_url']}")
            print(f"📦 ID: {release_data['id']}")
            
            # 4. Upload dos assets
            upload_assets(release_data)
            
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
            # Tentar método alternativo
            return try_alternative_method()
            
    except Exception as e:
        print(f"❌ Erro na criação: {e}")
        return try_alternative_method()

def upload_assets(release_data):
    """Fazer upload dos assets para a release"""
    
    print("\n📦 Fazendo upload dos assets...")
    
    assets = [
        "release-assets/QUICK_START_v1.5.1.md",
        "release-assets/requirements.txt",
        "release-assets/pytest.ini",
        "release-assets/test_results_v1.5.0_final.json"
    ]
    
    upload_url_template = release_data['upload_url']
    upload_count = 0
    
    for asset_path in assets:
        if os.path.exists(asset_path):
            if upload_single_asset(upload_url_template, asset_path):
                upload_count += 1
        else:
            print(f"⚠️  Asset não encontrado: {asset_path}")
    
    print(f"\n📎 Upload concluído: {upload_count}/{len(assets)} assets")
    return upload_count

def upload_single_asset(upload_url_template, file_path):
    """Upload de um asset individual"""
    
    file_name = os.path.basename(file_path)
    upload_url = upload_url_template.replace('{?name,label}', f'?name={file_name}')
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-RAG-Release-Creator",
        "Content-Type": "application/octet-stream"
    }
    
    try:
        print(f"📎 Uploading: {file_name}")
        
        with open(file_path, 'rb') as f:
            response = requests.post(upload_url, headers=headers, data=f)
        
        if response.status_code == 201:
            print(f"✅ Upload concluído: {file_name}")
            return True
        else:
            print(f"❌ Erro no upload de {file_name}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no upload de {file_name}: {e}")
        return False

def try_alternative_method():
    """Método alternativo usando curl se disponível"""
    
    print("\n🔄 Tentando método alternativo...")
    
    import subprocess
    
    # Verificar se curl está disponível
    try:
        result = subprocess.run(["curl", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ curl encontrado, tentando via curl...")
            return create_with_curl()
        else:
            print("❌ curl não disponível")
            return show_manual_instructions()
    except FileNotFoundError:
        print("❌ curl não instalado")
        return show_manual_instructions()

def create_with_curl():
    """Criar release usando curl"""
    
    import subprocess
    import tempfile
    
    try:
        # Criar arquivo temporário com release notes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            release_data = {
                "tag_name": TAG_NAME,
                "target_commitish": "main",
                "name": RELEASE_NAME,
                "body": open("release-assets/RELEASE_NOTES_v1.5.1.md", "r", encoding="utf-8").read(),
                "draft": False,
                "prerelease": False
            }
            json.dump(release_data, f)
            temp_file = f.name
        
        # Comando curl
        cmd = [
            "curl",
            "-X", "POST",
            f"https://api.github.com/repos/{OWNER}/{REPO}/releases",
            "-H", "Accept: application/vnd.github.v3+json",
            "-H", "User-Agent: curl-RAG-Release",
            "-d", f"@{temp_file}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Limpar arquivo temporário
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print("🎉 Release criada via curl!")
            response_data = json.loads(result.stdout)
            print(f"🔗 URL: {response_data['html_url']}")
            return True
        else:
            print(f"❌ Erro no curl: {result.stderr}")
            return show_manual_instructions()
            
    except Exception as e:
        print(f"❌ Erro no método curl: {e}")
        return show_manual_instructions()

def show_manual_instructions():
    """Mostrar instruções manuais detalhadas"""
    
    print("\n📋 INSTRUÇÕES PARA CRIAÇÃO MANUAL:")
    print("=" * 50)
    print(f"1. 🔗 Acesse: https://github.com/{OWNER}/{REPO}/releases/new")
    print(f"2. 🏷️  Tag: {TAG_NAME}")
    print(f"3. 📝 Title: {RELEASE_NAME}")
    print("4. 📄 Description: Cole o conteúdo completo de:")
    print("   release-assets/RELEASE_NOTES_v1.5.1.md")
    print("5. 📎 Assets: Arraste os arquivos:")
    
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
    
    print("6. ⚙️  Configurações:")
    print("   ✅ Marque 'Set as the latest release'")
    print("   ❌ NÃO marque 'This is a pre-release'")
    print("7. 🚀 Clique 'Publish release'")
    
    return False

def verify_final_result():
    """Verificar se a release foi criada com sucesso"""
    
    print("\n🔍 Verificação final...")
    
    try:
        response = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/releases")
        releases = response.json()
        
        if len(releases) > 0:
            print(f"✅ {len(releases)} release(s) encontrada(s):")
            for rel in releases:
                print(f"   📦 {rel['name']} ({rel['tag_name']})")
                print(f"   🔗 {rel['html_url']}")
                print(f"   📎 {len(rel.get('assets', []))} assets")
                print()
            return True
        else:
            print("❌ Nenhuma release encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    
    # Tentar criar release
    success = create_release_complete()
    
    # Aguardar um pouco para propagação
    if success:
        print("\n⏳ Aguardando propagação...")
        time.sleep(3)
    
    # Verificar resultado final
    verify_final_result()
    
    if success:
        print("\n🎊 SUCESSO TOTAL!")
        print("🚀 RAG Python v1.5.1 está oficialmente publicado!")
        print(f"🔗 Acesse: https://github.com/{OWNER}/{REPO}/releases")
    else:
        print("\n💡 Siga as instruções manuais acima para completar a publicação")

if __name__ == "__main__":
    main() 