#!/usr/bin/env python3
"""
Script de instalação e configuração do Sistema RAG Python
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Exibe o banner do projeto"""
    print("""
🤖 Sistema RAG Python - Setup
=============================
""")

def check_python_version():
    """Verifica a versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def install_dependencies():
    """Instala as dependências do projeto"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_env_file():
    """Cria arquivo .env se não existir"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("\n🔧 Criando arquivo .env...")
        shutil.copy(env_example, env_file)
        print("✅ Arquivo .env criado!")
        print("⚠️  IMPORTANTE: Edite o arquivo .env com sua chave da OpenAI")
        return True
    elif env_file.exists():
        print("✅ Arquivo .env já existe")
        return True
    else:
        print("❌ Arquivo env.example não encontrado")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    directories = ["documents", "vector_db"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Diretório {directory}/ criado")

def test_installation():
    """Testa a instalação"""
    print("\n🧪 Testando instalação...")
    try:
        # Testar importação dos módulos principais
        import langchain
        import openai
        import streamlit
        import chromadb
        print("✅ Módulos principais importados com sucesso!")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        return False

def show_next_steps():
    """Mostra os próximos passos"""
    print("""
🎉 Instalação concluída!

📋 Próximos passos:

1. Configure sua API key da OpenAI:
   - Edite o arquivo .env
   - Adicione sua chave: OPENAI_API_KEY=sua_chave_aqui

2. Teste o sistema:
   python example.py

3. Execute a interface web:
   streamlit run app.py

4. Adicione documentos:
   - Coloque arquivos PDF, DOCX ou TXT na pasta documents/
   - Ou use a interface web para fazer upload

📚 Documentação:
   - README.md - Guia principal
   - DOCUMENTATION.md - Documentação técnica

🤝 Suporte:
   - GitHub: https://github.com/jessefreitas/rag_python
   - Issues: Para reportar problemas
""")

def main():
    """Função principal"""
    print_banner()
    
    # Verificar versão do Python
    if not check_python_version():
        sys.exit(1)
    
    # Instalar dependências
    if not install_dependencies():
        sys.exit(1)
    
    # Criar arquivo .env
    create_env_file()
    
    # Criar diretórios
    create_directories()
    
    # Testar instalação
    if not test_installation():
        print("⚠️  Aviso: Alguns módulos não puderam ser importados")
    
    # Mostrar próximos passos
    show_next_steps()

if __name__ == "__main__":
    main() 