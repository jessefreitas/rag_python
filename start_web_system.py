"""
Script de inicialização do Sistema Web de Agentes RAG
Facilita a configuração e execução do sistema
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'flask',
        'flask_cors', 
        'werkzeug',
        'openai',
        'langchain',
        'langchain_openai',
        'langchain_community',
        'sentence_transformers',
        'faiss_cpu',
        'chromadb'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - não instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        install = input("Deseja instalar automaticamente? (s/n): ").lower()
        
        if install == 's':
            print("📦 Instalando dependências...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                print("✅ Dependências instaladas com sucesso!")
                return True
            except subprocess.CalledProcessError:
                print("❌ Erro ao instalar dependências")
                return False
        else:
            print("❌ Instale as dependências manualmente antes de continuar")
            return False
    
    return True

def check_environment():
    """Verifica configuração do ambiente"""
    print("\n🔧 Verificando configuração do ambiente...")
    
    # Verificar OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY não configurada")
        
        # Tentar carregar do arquivo .env
        env_file = Path(".env")
        if env_file.exists():
            print("📄 Arquivo .env encontrado, carregando...")
            from dotenv import load_dotenv
            load_dotenv()
            
            if not os.getenv("OPENAI_API_KEY"):
                print("❌ OPENAI_API_KEY não encontrada no arquivo .env")
                return False
        else:
            print("❌ Arquivo .env não encontrado")
            return False
    
    print("✅ OPENAI_API_KEY configurada")
    
    # Criar pastas necessárias
    folders = ['agent_uploads', 'agent_vector_dbs', 'templates', 'temp']
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"✅ Pasta {folder}/ criada/verificada")
    
    return True

def show_welcome():
    """Mostra mensagem de boas-vindas"""
    print("""
🤖 SISTEMA WEB DE AGENTES RAG
================================

Este sistema permite:
• Criar agentes de IA personalizados
• Upload de documentos para cada agente
• Chat individual com cada agente
• Gerenciamento via interface web
• Isolamento de conhecimento por agente

📁 Estrutura criada:
• agent_uploads/     - Documentos por agente
• agent_vector_dbs/  - Bancos de vetores
• templates/         - Interface web
• temp/             - Arquivos temporários

🌐 Acesso:
• Dashboard: http://localhost:5000
• Gerenciar Agentes: http://localhost:5000/agents

""")

def start_server():
    """Inicia o servidor web"""
    print("\n🚀 Iniciando servidor web...")
    print("📡 Servidor rodando em: http://localhost:5000")
    print("⏹️  Pressione Ctrl+C para parar\n")
    
    try:
        from web_agent_manager import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def main():
    """Função principal"""
    print("🤖 Inicializando Sistema Web de Agentes RAG...")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Falha na verificação de dependências")
        return
    
    # Verificar ambiente
    if not check_environment():
        print("\n❌ Falha na configuração do ambiente")
        return
    
    # Mostrar boas-vindas
    show_welcome()
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main() 