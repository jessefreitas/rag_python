#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 RAG Python - Corretor Universal de Problemas
==================================================
Script para corrigir todos os problemas e rodar o sistema completo
"""

import os
import sys
import time
import json
import psutil
import subprocess
import importlib.util
from pathlib import Path

def print_header():
    """Exibe cabeçalho do script"""
    print("=" * 70)
    print("🔧 RAG PYTHON v1.5.1 - CORRETOR UNIVERSAL")
    print("=" * 70)
    print("🎯 Corrigindo todos os problemas e iniciando sistema completo")
    print("=" * 70)

def kill_processes_on_port(port):
    """Mata processos rodando em uma porta específica"""
    try:
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                connections = proc.info['connections']
                if connections:
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            print(f"  🔫 Matando processo {proc.info['name']} (PID: {proc.info['pid']}) na porta {port}")
                            proc.kill()
                            killed_count += 1
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if killed_count > 0:
            print(f"  ✅ {killed_count} processo(s) encerrado(s) na porta {port}")
        else:
            print(f"  ✅ Porta {port} livre")
        return True
    except Exception as e:
        print(f"  ⚠️ Erro ao verificar porta {port}: {e}")
        return False

def check_and_fix_llm_models_config():
    """Verifica e corrige o arquivo llm_models_config.py"""
    print("\n🔧 VERIFICANDO llm_models_config.py...")
    
    try:
        # Tentar importar
        import llm_models_config
        importlib.reload(llm_models_config)
        
        # Verificar se tem o método necessário
        if hasattr(llm_models_config.models_manager, 'get_provider_models_simple'):
            print("  ✅ llm_models_config.py OK - método get_provider_models_simple encontrado")
            return True
        else:
            print("  ❌ Método get_provider_models_simple não encontrado")
            return False
            
    except SyntaxError as e:
        print(f"  ❌ Erro de sintaxe em llm_models_config.py: {e}")
        print("  🔄 Recriando arquivo...")
        
        # Recriar arquivo limpo
        recreate_llm_models_config()
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao importar llm_models_config.py: {e}")
        return False

def recreate_llm_models_config():
    """Recria o arquivo llm_models_config.py completamente limpo"""
    content = '''# -*- coding: utf-8 -*-
"""
🤖 RAG Python - Configuração de Modelos LLM v1.5.3
==================================================
Catálogo completo de modelos de diferentes provedores
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class ModelInfo:
    """Informações de um modelo LLM"""
    name: str
    provider: str
    description: str
    context_length: int
    supports_vision: bool = False
    supports_function_calling: bool = False
    cost_per_1k_tokens: float = 0.0
    emoji: str = "🤖"

class ModelsManager:
    """Gerenciador central de modelos LLM"""
    
    def __init__(self):
        self.models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Inicializa catálogo de modelos"""
        return {
            # OpenAI Models
            "gpt-4o": ModelInfo(
                name="gpt-4o",
                provider="openai",
                description="🚀 GPT-4o - Modelo mais avançado da OpenAI",
                context_length=128000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.005,
                emoji="🚀"
            ),
            "gpt-4o-mini": ModelInfo(
                name="gpt-4o-mini",
                provider="openai",
                description="⚡ GPT-4o Mini - Rápido e eficiente",
                context_length=128000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.00015,
                emoji="⚡"
            ),
            "gpt-4-turbo": ModelInfo(
                name="gpt-4-turbo",
                provider="openai",
                description="🏎️ GPT-4 Turbo - Alto desempenho",
                context_length=128000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.01,
                emoji="🏎️"
            ),
            "gpt-3.5-turbo": ModelInfo(
                name="gpt-3.5-turbo",
                provider="openai",
                description="💨 GPT-3.5 Turbo - Rápido e confiável",
                context_length=16385,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0005,
                emoji="💨"
            ),
            
            # Google Models
            "gemini-1.5-pro": ModelInfo(
                name="gemini-1.5-pro",
                provider="google",
                description="💎 Gemini 1.5 Pro - Modelo premium do Google",
                context_length=2000000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0035,
                emoji="💎"
            ),
            "gemini-1.5-flash": ModelInfo(
                name="gemini-1.5-flash",
                provider="google",
                description="⚡ Gemini 1.5 Flash - Ultrarrápido",
                context_length=1000000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.00015,
                emoji="⚡"
            ),
            "gemini-pro": ModelInfo(
                name="gemini-pro",
                provider="google",
                description="🌟 Gemini Pro - Modelo principal do Google",
                context_length=32768,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0005,
                emoji="🌟"
            ),
            
            # OpenRouter Models
            "anthropic/claude-3.5-sonnet": ModelInfo(
                name="anthropic/claude-3.5-sonnet",
                provider="openrouter",
                description="🎼 Claude 3.5 Sonnet - Excelente para escrita",
                context_length=200000,
                supports_function_calling=True,
                cost_per_1k_tokens=0.003,
                emoji="🎼"
            ),
            "openai/gpt-4o": ModelInfo(
                name="openai/gpt-4o",
                provider="openrouter",
                description="🚀 GPT-4o via OpenRouter",
                context_length=128000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.005,
                emoji="🚀"
            ),
            
            # DeepSeek Models
            "deepseek-chat": ModelInfo(
                name="deepseek-chat",
                provider="deepseek",
                description="🔮 DeepSeek Chat - Conversação avançada",
                context_length=32768,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0001,
                emoji="🔮"
            ),
            "deepseek-coder": ModelInfo(
                name="deepseek-coder",
                provider="deepseek",
                description="💻 DeepSeek Coder - Especialista em programação",
                context_length=16384,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0001,
                emoji="💻"
            )
        }
    
    def get_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """Retorna modelos de um provedor específico"""
        return [model for model in self.models.values() if model.provider == provider]
    
    def get_model_info(self, model_name: str) -> ModelInfo:
        """Retorna informações de um modelo específico"""
        return self.models.get(model_name)
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        providers = set(model.provider for model in self.models.values())
        return sorted(list(providers))
    
    def get_provider_models_simple(self) -> Dict[str, List[str]]:
        """Retorna dicionário simples de modelos por provedor"""
        result = {}
        for provider in self.get_available_providers():
            result[provider] = [model.name for model in self.get_models_by_provider(provider)]
        return result
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estatísticas por provedor"""
        stats = {}
        for provider in self.get_available_providers():
            provider_models = self.get_models_by_provider(provider)
            stats[provider] = {
                'total_models': len(provider_models),
                'models': [m.name for m in provider_models]
            }
        return stats

# Instância global do gerenciador
models_manager = ModelsManager()

# Mapeamento de compatibilidade
PROVIDER_MODEL_MAP = {
    'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    'google': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],
    'openrouter': ['anthropic/claude-3.5-sonnet', 'openai/gpt-4o'],
    'deepseek': ['deepseek-chat', 'deepseek-coder']
}

if __name__ == "__main__":
    print("🤖 RAG Python - Catálogo de Modelos LLM v1.5.3")
    print("=" * 50)
    
    stats = models_manager.get_provider_stats()
    for provider, data in stats.items():
        print(f"📊 {provider.upper()}: {data['total_models']} modelos")
    
    print(f"✅ Total: {len(models_manager.models)} modelos carregados")
'''
    
    with open('llm_models_config.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ Arquivo llm_models_config.py recriado com sucesso")

def check_environment():
    """Verifica variáveis de ambiente"""
    print("\n🔧 VERIFICANDO VARIÁVEIS DE AMBIENTE...")
    
    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY')
    }
    
    configured = 0
    for var, value in env_vars.items():
        if value:
            print(f"  ✅ {var} configurada")
            configured += 1
        else:
            print(f"  ❌ {var} não configurada")
    
    print(f"  📊 {configured}/4 provedores configurados")
    return configured > 0

def start_server(script_name, port, name, background=True):
    """Inicia um servidor em background"""
    print(f"\n🚀 INICIANDO {name}...")
    
    # Matar processos existentes na porta
    kill_processes_on_port(port)
    time.sleep(2)
    
    try:
        if background:
            # Iniciar em background
            if sys.platform == "win32":
                process = subprocess.Popen(
                    ['python', script_name],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                process = subprocess.Popen(
                    ['python', script_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            time.sleep(3)  # Dar tempo para inicializar
            
            # Verificar se ainda está rodando
            if process.poll() is None:
                print(f"  ✅ {name} iniciado com sucesso na porta {port}")
                print(f"  📡 URL: http://localhost:{port}")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"  ❌ Erro ao iniciar {name}:")
                if stderr:
                    print(f"      {stderr.decode()[:200]}...")
                return False
        else:
            print(f"  📡 Executando: python {script_name}")
            print(f"  🌐 URL: http://localhost:{port}")
            print(f"  ⏹️ Pressione Ctrl+C para parar")
            subprocess.run(['python', script_name])
            return True
            
    except Exception as e:
        print(f"  ❌ Erro ao iniciar {name}: {e}")
        return False

def main():
    """Função principal"""
    print_header()
    
    # 1. Verificar e corrigir llm_models_config.py
    if not check_and_fix_llm_models_config():
        print("❌ Não foi possível corrigir llm_models_config.py")
        return False
    
    # 2. Verificar ambiente
    if not check_environment():
        print("⚠️ Nenhuma API key configurada, sistema funcionará em modo limitado")
    
    # 3. Limpar portas
    print("\n🧹 LIMPANDO PORTAS...")
    ports_to_clean = [8501, 5000, 5001, 5002]
    for port in ports_to_clean:
        kill_processes_on_port(port)
    
    print("\n" + "=" * 70)
    print("🎯 ESCOLHA O MODO DE INICIALIZAÇÃO:")
    print("=" * 70)
    print("1. 🚀 COMPLETO - Todos os servidores em background")
    print("2. 🎯 STREAMLIT - Apenas interface principal (porta 8501)")
    print("3. 🔌 API FLASK - Apenas API para extensão (porta 5000)")
    print("4. 🗄️ API SUPABASE - API com Supabase (porta 5002)")
    print("5. ⚙️ MANUAL - Escolher individualmente")
    print("=" * 70)
    
    try:
        choice = input("Digite sua escolha (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Operação cancelada pelo usuário")
        return
    
    if choice == "1":
        print("\n🚀 MODO COMPLETO - Iniciando todos os servidores...")
        
        # Iniciar todos em background
        servers = [
            ('api_server_simple.py', 5000, 'API Flask Simples'),
            ('api_server_supabase.py', 5002, 'API Supabase'),
        ]
        
        success_count = 0
        for script, port, name in servers:
            if start_server(script, port, name, background=True):
                success_count += 1
        
        print(f"\n📊 RESULTADO: {success_count}/{len(servers)} servidores iniciados")
        
        # Streamlit por último (foreground)
        print("\n🎯 Iniciando Streamlit (interface principal)...")
        start_server('iniciar_servidor_rag.py', 8501, 'Streamlit RAG', background=False)
        
    elif choice == "2":
        print("\n🎯 MODO STREAMLIT - Apenas interface principal...")
        start_server('iniciar_servidor_rag.py', 8501, 'Streamlit RAG', background=False)
        
    elif choice == "3":
        print("\n🔌 MODO API FLASK - Apenas API para extensão...")
        start_server('api_server_simple.py', 5000, 'API Flask', background=False)
        
    elif choice == "4":
        print("\n🗄️ MODO API SUPABASE - API com Supabase...")
        start_server('api_server_supabase.py', 5002, 'API Supabase', background=False)
        
    elif choice == "5":
        print("\n⚙️ MODO MANUAL - Escolha individual...")
        
        servers = [
            ('iniciar_servidor_rag.py', 8501, 'Streamlit RAG (Interface Principal)'),
            ('api_server_simple.py', 5000, 'API Flask Simples'),
            ('api_server_supabase.py', 5002, 'API Supabase'),
        ]
        
        for i, (script, port, name) in enumerate(servers, 1):
            resp = input(f"Iniciar {name}? (s/n): ").strip().lower()
            if resp in ['s', 'sim', 'y', 'yes']:
                bg = input("Em background? (s/n): ").strip().lower() not in ['s', 'sim', 'y', 'yes']
                start_server(script, port, name, background=not bg)
                if not bg:  # Se não é background, para aqui
                    break
    else:
        print("❌ Opção inválida")
        return
    
    print("\n" + "=" * 70)
    print("✅ SISTEMA RAG PYTHON INICIADO COM SUCESSO!")
    print("=" * 70)
    print("🌐 URLs disponíveis:")
    print("  - Streamlit: http://localhost:8501")
    print("  - API Flask: http://localhost:5000")
    print("  - API Supabase: http://localhost:5002")
    print("=" * 70)

if __name__ == "__main__":
    main() 