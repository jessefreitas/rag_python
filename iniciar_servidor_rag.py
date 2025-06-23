#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 INICIALIZADOR COMPLETO - RAG PYTHON v1.5.1
Script padronizado para iniciar o sistema RAG de forma robusta
"""

import os
import sys
import subprocess
import time
import signal
import psutil
import socket
from pathlib import Path
from typing import List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGServerManager:
    """Gerenciador para inicialização robusta do servidor RAG"""
    
    def __init__(self):
        self.port = 8501
        self.app_file = "app_completo_unificado.py"
        self.project_root = Path(__file__).parent
        self.required_files = [
            "app_completo_unificado.py",
            "llm_providers.py", 
            "database.py",
            "vector_store.py",
            "privacy_system.py"
        ]
        
    def banner(self):
        """Exibe banner de inicialização"""
        print("="*70)
        print("🚀 RAG PYTHON v1.5.1 - INICIALIZADOR COMPLETO")
        print("="*70)
        print("🎯 Sistema Unificado: Multi-LLM + Agentes + Privacidade")
        print("🔧 Inicialização robusta e padronizada")
        print("="*70)
    
    def check_dependencies(self) -> bool:
        """Verifica dependências críticas"""
        print("\n🔍 VERIFICANDO DEPENDÊNCIAS...")
        
        required_packages = [
            'streamlit',
            'openai', 
            'psycopg2',
            'chromadb',
            'langchain',
            'python-dotenv',
            'requests',
            'psutil'
        ]
        
        missing = []
        for package in required_packages:
            try:
                # Tratamento especial para python-dotenv
                if package == 'python-dotenv':
                    __import__('dotenv')
                else:
                    __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} - FALTANDO")
                missing.append(package)
        
        if missing:
            print(f"\n⚠️  Pacotes faltando: {', '.join(missing)}")
            install = input("Instalar automaticamente? (s/n): ").lower()
            if install == 's':
                return self.install_dependencies(missing)
            else:
                print("❌ Instale as dependências manualmente")
                return False
        
        print("✅ Todas as dependências OK")
        return True
    
    def install_dependencies(self, packages: List[str]) -> bool:
        """Instala dependências automaticamente"""
        print(f"\n📦 INSTALANDO: {', '.join(packages)}")
        
        # Tentar instalar via requirements_minimal.txt primeiro
        minimal_req = self.project_root / "requirements_minimal.txt"
        if minimal_req.exists():
            print("📋 Usando requirements_minimal.txt...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(minimal_req)])
                print("✅ Dependências mínimas instaladas com sucesso!")
                return True
            except subprocess.CalledProcessError:
                print("⚠️ Falha com requirements_minimal.txt, tentando instalação individual...")
        
        # Fallback para instalação individual
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
            print("✅ Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False
    
    def check_required_files(self) -> bool:
        """Verifica se arquivos críticos existem"""
        print("\n📁 VERIFICANDO ARQUIVOS CRÍTICOS...")
        
        missing_files = []
        for file in self.required_files:
            file_path = self.project_root / file
            if file_path.exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - NÃO ENCONTRADO")
                missing_files.append(file)
        
        if missing_files:
            print(f"\n❌ Arquivos faltando: {', '.join(missing_files)}")
            return False
        
        print("✅ Todos os arquivos críticos encontrados")
        return True
    
    def fix_encoding_issues(self):
        """Corrige problemas de encoding nos arquivos"""
        print("\n🔧 CORRIGINDO PROBLEMAS DE ENCODING...")
        
        problematic_files = [
            "llm_models_config.py",
            "app_completo_unificado.py"
        ]
        
        for filename in problematic_files:
            file_path = self.project_root / filename
            if not file_path.exists():
                continue
                
            try:
                # Ler arquivo com encoding correto
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Remover null bytes se existirem
                if '\x00' in content:
                    print(f"  🔧 Removendo null bytes de {filename}")
                    content = content.replace('\x00', '')
                    
                    # Reescrever arquivo limpo
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✅ {filename} corrigido")
                else:
                    print(f"  ✅ {filename} OK")
                    
            except Exception as e:
                print(f"  ⚠️ Erro ao processar {filename}: {e}")
    
    def check_environment(self) -> bool:
        """Verifica configuração do ambiente"""
        print("\n🔧 VERIFICANDO CONFIGURAÇÃO DO AMBIENTE...")
        
        # Carregar .env se existir
        env_file = self.project_root / ".env"
        if env_file.exists():
            print("  📄 Arquivo .env encontrado")
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                print("  ✅ Variáveis de ambiente carregadas")
            except ImportError:
                print("  ⚠️ python-dotenv não instalado")
        
        # Verificar API keys principais
        api_keys = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
            'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
            'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY')
        }
        
        configured_keys = 0
        for key, value in api_keys.items():
            if value:
                print(f"  ✅ {key} configurada")
                configured_keys += 1
            else:
                print(f"  ⚠️ {key} não configurada")
        
        if configured_keys == 0:
            print("  ❌ Nenhuma API key configurada!")
            return False
        
        print(f"  📊 {configured_keys}/4 provedores configurados")
        return True
    
    def kill_existing_servers(self):
        """Para servidores existentes na porta"""
        print(f"\n🛑 PARANDO SERVIDORES EXISTENTES NA PORTA {self.port}...")
        
        # Verificar se porta está em uso
        if not self.is_port_in_use(self.port):
            print(f"  ✅ Porta {self.port} livre")
            return
        
        # Matar processos na porta
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('streamlit' in cmd for cmd in cmdline):
                    if any(str(self.port) in cmd for cmd in cmdline):
                        print(f"  🔫 Matando processo Streamlit PID {proc.info['pid']}")
                        proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if killed:
            time.sleep(2)  # Aguardar processos morrerem
            print(f"  ✅ Servidores na porta {self.port} encerrados")
        else:
            print(f"  ⚠️ Nenhum servidor Streamlit encontrado na porta {self.port}")
    
    def is_port_in_use(self, port: int) -> bool:
        """Verifica se uma porta está em uso"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except socket.error:
                return True
    
    def start_server(self):
        """Inicia o servidor Streamlit"""
        print(f"\n🚀 INICIANDO SERVIDOR RAG NA PORTA {self.port}...")
        
        # Comando para iniciar Streamlit
        cmd = [
            'streamlit', 'run', 
            str(self.app_file),
            '--server.port', str(self.port),
            '--server.address', 'localhost',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'
        ]
        
        try:
            print(f"  📡 Comando: {' '.join(cmd)}")
            print(f"  🌐 URL Local: http://localhost:{self.port}")
            print(f"  🔗 URL de Rede: http://127.0.0.1:{self.port}")
            print("\n  ⏹️  Pressione Ctrl+C para parar o servidor")
            print("  " + "="*50)
            
            # Executar comando
            subprocess.run(cmd, cwd=self.project_root)
            
        except KeyboardInterrupt:
            print("\n\n👋 Servidor parado pelo usuário")
        except FileNotFoundError:
            print("❌ Streamlit não encontrado. Instale com: pip install streamlit")
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
    
    def run(self):
        """Executa todo o processo de inicialização"""
        self.banner()
        
        # 1. Verificar dependências
        if not self.check_dependencies():
            print("\n❌ Falha na verificação de dependências")
            return False
        
        # 2. Verificar arquivos
        if not self.check_required_files():
            print("\n❌ Arquivos críticos não encontrados")
            return False
        
        # 3. Corrigir problemas de encoding
        self.fix_encoding_issues()
        
        # 4. Verificar ambiente
        if not self.check_environment():
            print("\n⚠️ Ambiente não está totalmente configurado, mas continuando...")
        
        # 5. Parar servidores existentes
        self.kill_existing_servers()
        
        # 6. Aguardar um pouco
        print("\n⏱️ Aguardando 3 segundos...")
        time.sleep(3)
        
        # 7. Iniciar servidor
        self.start_server()
        
        return True

def main():
    """Função principal"""
    try:
        manager = RAGServerManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 Inicialização interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        logger.exception("Erro na inicialização")

if __name__ == "__main__":
    main() 