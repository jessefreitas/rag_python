import requests
import json

def check_releases():
    url = "https://api.github.com/repos/jessefreitas/rag_python/releases"
    
    try:
        response = requests.get(url)
        releases = response.json()
        
        print(f"🔍 Status da API: {response.status_code}")
        print(f"📦 Releases encontradas: {len(releases)}")
        
        if len(releases) == 0:
            print("❌ Nenhuma release encontrada!")
            print("💡 A release precisa ser criada manualmente no GitHub")
            print("🔗 Acesse: https://github.com/jessefreitas/rag_python/releases/new")
        else:
            print("\n✅ Releases disponíveis:")
            for i, rel in enumerate(releases, 1):
                print(f"{i}. {rel['name']} ({rel['tag_name']})")
                print(f"   📅 Criada: {rel['created_at']}")
                print(f"   🔗 URL: {rel['html_url']}")
                print()
                
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_releases() 