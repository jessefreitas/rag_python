import requests

def check_release_details():
    url = "https://api.github.com/repos/jessefreitas/rag_python/releases"
    
    try:
        response = requests.get(url)
        releases = response.json()
        
        if len(releases) > 0:
            rel = releases[0]  # Primeira release (mais recente)
            
            print("🎯 DETALHES DA RELEASE:")
            print("=" * 50)
            print(f"📦 Nome: {rel['name']}")
            print(f"🏷️ Tag: {rel['tag_name']}")
            print(f"🔗 URL: {rel['html_url']}")
            print(f"📅 Criada: {rel['created_at']}")
            print(f"📊 Downloads ZIP: {rel['zipball_url']}")
            print(f"📊 Downloads TAR: {rel['tarball_url']}")
            print(f"✅ Latest: {rel.get('latest', 'N/A')}")
            print(f"📎 Assets: {len(rel['assets'])}")
            
            if rel['assets']:
                print("\n📎 ASSETS ANEXADOS:")
                for i, asset in enumerate(rel['assets'], 1):
                    print(f"   {i}. {asset['name']}")
                    print(f"      📏 Tamanho: {asset['size']} bytes")
                    print(f"      📥 Downloads: {asset['download_count']}")
                    print(f"      🔗 URL: {asset['browser_download_url']}")
                    print()
            else:
                print("⚠️  Nenhum asset anexado")
            
            print("\n🎊 RELEASE PUBLICADA COM SUCESSO!")
            print("🚀 RAG Python v1.5.1 está oficialmente disponível!")
            
        else:
            print("❌ Nenhuma release encontrada")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_release_details() 