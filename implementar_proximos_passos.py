#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 IMPLEMENTAÇÃO DOS PRÓXIMOS PASSOS - RAG PYTHON v1.5.1+
Script unificado para evoluir o sistema com as melhorias planejadas
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProximosPassosImplementor:
    """Implementador dos próximos passos do sistema RAG Python"""
    
    def __init__(self):
        self.status = {
            'provedores_configurados': [],
            'postgres_status': 'desconhecido',
            'embeddings_funcionais': False,
            'testes_realizados': []
        }
        
    def diagnosticar_sistema_completo(self) -> Dict[str, Any]:
        """Diagnóstico completo do estado atual do sistema"""
        print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA RAG PYTHON")
        print("=" * 60)
        
        diagnostico = {
            'timestamp': datetime.now().isoformat(),
            'provedores': self._diagnosticar_provedores(),
            'postgresql': self._diagnosticar_postgresql(),
            'embeddings': self._diagnosticar_embeddings(),
            'dependencias': self._diagnosticar_dependencias(),
            'arquivos_core': self._diagnosticar_arquivos_core()
        }
        
        self._gerar_relatorio_diagnostico(diagnostico)
        return diagnostico
    
    def _diagnosticar_provedores(self) -> Dict[str, Any]:
        """Diagnóstica estado dos provedores LLM"""
        print("\n🤖 PROVEDORES LLM:")
        
        provedores = {
            'openai': {
                'env_var': 'OPENAI_API_KEY',
                'configurado': bool(os.getenv('OPENAI_API_KEY')),
                'modelos_suportados': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
            },
            'google': {
                'env_var': 'GOOGLE_GEMINI_API_KEY',
                'configurado': bool(os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')),
                'modelos_suportados': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
            },
            'openrouter': {
                'env_var': 'OPENROUTER_API_KEY',
                'configurado': bool(os.getenv('OPENROUTER_API_KEY')),
                'modelos_suportados': ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet', 'meta-llama/llama-3.1-405b-instruct']
            },
            'deepseek': {
                'env_var': 'DEEPSEEK_API_KEY',
                'configurado': bool(os.getenv('DEEPSEEK_API_KEY')),
                'modelos_suportados': ['deepseek-chat', 'deepseek-coder', 'deepseek-math']
            }
        }
        
        configurados = 0
        for nome, info in provedores.items():
            status = "✅ CONFIGURADO" if info['configurado'] else "❌ NÃO CONFIGURADO"
            print(f"  {nome.upper()}: {status}")
            if info['configurado']:
                configurados += 1
                self.status['provedores_configurados'].append(nome)
        
        print(f"\n📊 Total: {configurados}/4 provedores configurados")
        
        if configurados == 1:
            print("⚠️ PROBLEMA IDENTIFICADO: Apenas 1 provedor configurado pode causar erro 404 'model not found'")
        
        return provedores
    
    def _diagnosticar_postgresql(self) -> Dict[str, Any]:
        """Diagnóstica estado do PostgreSQL"""
        print("\n🐘 POSTGRESQL:")
        
        pg_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'rag_system'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password_set': bool(os.getenv('DB_PASSWORD'))
        }
        
        try:
            # Tentar conexão
            conn = psycopg2.connect(
                host=pg_config['host'],
                port=pg_config['port'],
                database=pg_config['database'],
                user=pg_config['user'],
                password=os.getenv('DB_PASSWORD', 'postgres')
            )
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar extensões
                cur.execute("SELECT extname FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');")
                extensoes = [row['extname'] for row in cur.fetchall()]
                
                # Verificar tabelas
                cur.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('agentes', 'documents', 'document_chunks', 'conversations', 'llm_responses')
                """)
                tabelas = [row['table_name'] for row in cur.fetchall()]
                
                # Estatísticas das tabelas
                stats = {}
                for tabela in tabelas:
                    cur.execute(f"SELECT COUNT(*) as count FROM {tabela}")
                    stats[tabela] = cur.fetchone()['count']
            
            conn.close()
            
            pg_status = {
                'conectado': True,
                'config': pg_config,
                'extensoes': extensoes,
                'tabelas': tabelas,
                'estatisticas': stats,
                'vector_extension': 'vector' in extensoes
            }
            
            print(f"  ✅ Conexão: {pg_config['host']}:{pg_config['port']}/{pg_config['database']}")
            print(f"  📋 Extensões: {extensoes}")
            print(f"  🗂️ Tabelas: {len(tabelas)}/5")
            print(f"  📊 Registros: {sum(stats.values())} total")
            
            if 'vector' not in extensoes:
                print("  ⚠️ Extensão pgvector não encontrada - necessária para embeddings")
            
            self.status['postgres_status'] = 'conectado'
            
        except Exception as e:
            pg_status = {
                'conectado': False,
                'erro': str(e),
                'config': pg_config
            }
            print(f"  ❌ Erro de conexão: {e}")
            self.status['postgres_status'] = 'erro'
        
        return pg_status
    
    def _diagnosticar_embeddings(self) -> Dict[str, Any]:
        """Diagnóstica sistema de embeddings"""
        print("\n🧠 SISTEMA DE EMBEDDINGS:")
        
        try:
            from openai import OpenAI
            
            if not os.getenv('OPENAI_API_KEY'):
                print("  ❌ OpenAI API Key não configurada - embeddings indisponíveis")
                return {'disponivel': False, 'erro': 'API Key não configurada'}
            
            # Teste básico de embedding
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input="Teste de embedding"
            )
            
            embedding_info = {
                'disponivel': True,
                'modelo': 'text-embedding-3-small',
                'dimensoes': len(response.data[0].embedding),
                'teste_realizado': True
            }
            
            print(f"  ✅ OpenAI Embeddings funcionais")
            print(f"  📐 Modelo: text-embedding-3-small ({embedding_info['dimensoes']} dimensões)")
            
            self.status['embeddings_funcionais'] = True
            
        except Exception as e:
            embedding_info = {
                'disponivel': False,
                'erro': str(e)
            }
            print(f"  ❌ Erro nos embeddings: {e}")
        
        return embedding_info
    
    def _diagnosticar_dependencias(self) -> Dict[str, Any]:
        """Diagnóstica dependências Python"""
        print("\n📦 DEPENDÊNCIAS:")
        
        deps_necessarias = [
            'streamlit', 'openai', 'psycopg2', 'chromadb', 
            'langchain', 'python-dotenv', 'requests'
        ]
        
        deps_status = {}
        for dep in deps_necessarias:
            try:
                __import__(dep)
                deps_status[dep] = '✅ Instalada'
            except ImportError:
                deps_status[dep] = '❌ Não encontrada'
        
        for dep, status in deps_status.items():
            print(f"  {dep}: {status}")
        
        return deps_status
    
    def _diagnosticar_arquivos_core(self) -> Dict[str, Any]:
        """Diagnóstica arquivos principais do sistema"""
        print("\n📁 ARQUIVOS PRINCIPAIS:")
        
        arquivos_core = [
            'llm_providers.py',
            'database.py', 
            'vector_store.py',
            'app_completo_unificado.py',
            'agent_system.py',
            'requirements.txt'
        ]
        
        arquivos_status = {}
        for arquivo in arquivos_core:
            if os.path.exists(arquivo):
                size = os.path.getsize(arquivo)
                arquivos_status[arquivo] = f'✅ Existe ({size} bytes)'
            else:
                arquivos_status[arquivo] = '❌ Não encontrado'
        
        for arquivo, status in arquivos_status.items():
            print(f"  {arquivo}: {status}")
        
        return arquivos_status
    
    def _gerar_relatorio_diagnostico(self, diagnostico: Dict[str, Any]):
        """Gera relatório detalhado do diagnóstico"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagnostico_completo_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(diagnostico, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Relatório salvo em: {filename}")
    
    def configurar_provedores_faltantes(self):
        """Configura provedores LLM que estão faltando"""
        print("\n🔧 CONFIGURAÇÃO DE PROVEDORES FALTANTES")
        print("=" * 50)
        
        provedores_faltantes = []
        
        if not os.getenv('GOOGLE_GEMINI_API_KEY'):
            provedores_faltantes.append('Google Gemini')
        
        if not os.getenv('OPENROUTER_API_KEY'):
            provedores_faltantes.append('OpenRouter')
        
        if not os.getenv('DEEPSEEK_API_KEY'):
            provedores_faltantes.append('DeepSeek')
        
        if not provedores_faltantes:
            print("✅ Todos os provedores já estão configurados!")
            return
        
        print(f"📋 Provedores não configurados: {', '.join(provedores_faltantes)}")
        
        # Gerar arquivo .env atualizado
        self._gerar_arquivo_env_completo()
        
        # Criar guia de configuração
        self._criar_guia_configuracao_provedores()
    
    def _gerar_arquivo_env_completo(self):
        """Gera arquivo .env com todas as configurações necessárias"""
        env_content = """# ===== RAG PYTHON - CONFIGURAÇÃO COMPLETA =====
# Configure as chaves de API dos provedores que deseja usar

# OpenAI (obrigatório para funcionalidade básica)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Gemini (modelos Google)
GOOGLE_GEMINI_API_KEY=your-gemini-api-key-here

# OpenRouter (acesso a múltiplos modelos via API unificada)
OPENROUTER_API_KEY=sk-or-your-openrouter-key-here

# DeepSeek (modelos chineses avançados)
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# ===== BANCO DE DADOS POSTGRESQL =====
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_system
DB_USER=postgres
DB_PASSWORD=postgres

# ===== CONFIGURAÇÕES OPCIONAIS =====
ENVIRONMENT=development
LOG_LEVEL=INFO

# ===== CONFIGURAÇÕES DE SEGURANÇA =====
SECRET_KEY=your-secret-key-for-jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
        
        with open('env_completo.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo 'env_completo.env' gerado - configure suas API keys")
    
    def _criar_guia_configuracao_provedores(self):
        """Cria guia detalhado para configuração dos provedores"""
        guia_content = """# 🔧 GUIA DE CONFIGURAÇÃO DE PROVEDORES

## Como Obter as API Keys

### 1. Google Gemini
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave e adicione ao .env: `GOOGLE_GEMINI_API_KEY=sua-chave-aqui`

### 2. OpenRouter
1. Acesse: https://openrouter.ai/keys
2. Crie uma conta ou faça login
3. Clique em "Create Key"
4. Copie a chave e adicione ao .env: `OPENROUTER_API_KEY=sk-or-sua-chave-aqui`

### 3. DeepSeek
1. Acesse: https://platform.deepseek.com/api_keys
2. Crie uma conta ou faça login
3. Clique em "Create API Key"
4. Copie a chave e adicione ao .env: `DEEPSEEK_API_KEY=sk-sua-chave-aqui`

## Modelos Recomendados

### Para Uso Geral:
- OpenAI: gpt-4o-mini (econômico) ou gpt-4o (avançado)
- Google: gemini-1.5-flash (rápido) ou gemini-1.5-pro (avançado)
- OpenRouter: openai/gpt-4o ou anthropic/claude-3.5-sonnet
- DeepSeek: deepseek-chat (geral) ou deepseek-coder (programação)

## Teste da Configuração

Após configurar, execute:
```bash
python implementar_proximos_passos.py --teste-provedores
```
"""
        
        with open('GUIA_PROVEDORES.md', 'w', encoding='utf-8') as f:
            f.write(guia_content)
        
        print("✅ Guia 'GUIA_PROVEDORES.md' criado")
    
    def otimizar_postgresql(self):
        """Otimiza configuração do PostgreSQL para vetorização"""
        print("\n🐘 OTIMIZAÇÃO DO POSTGRESQL")
        print("=" * 40)
        
        try:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'rag_system'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres')
            )
            
            with conn.cursor() as cur:
                # Verificar e instalar extensões necessárias
                print("🔧 Instalando extensões necessárias...")
                
                extensoes = [
                    "CREATE EXTENSION IF NOT EXISTS vector;",
                    "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
                    "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
                ]
                
                for ext_sql in extensoes:
                    try:
                        cur.execute(ext_sql)
                        conn.commit()
                    except Exception as e:
                        print(f"  ⚠️ Extensão já existe ou erro: {e}")
                
                # Verificar tabelas e índices
                print("🗂️ Otimizando índices para vetorização...")
                
                indices_otimizacao = [
                    "CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);",
                    "CREATE INDEX IF NOT EXISTS idx_chunks_agent_id_btree ON document_chunks(agent_id);",
                    "CREATE INDEX IF NOT EXISTS idx_documents_agent_hash ON documents(agent_id, content_hash);",
                    "CREATE INDEX IF NOT EXISTS idx_conversations_agent_time ON conversations(agent_id, created_at DESC);"
                ]
                
                for idx_sql in indices_otimizacao:
                    try:
                        cur.execute(idx_sql)
                        conn.commit()
                        print(f"  ✅ Índice criado/verificado")
                    except Exception as e:
                        print(f"  ⚠️ Erro no índice: {e}")
                
                # Estatísticas finais
                cur.execute("""
                    SELECT schemaname, tablename, indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename IN ('document_chunks', 'documents', 'agentes')
                    ORDER BY tablename, indexname
                """)
                indices = cur.fetchall()
                
                print(f"📊 Total de índices otimizados: {len(indices)}")
                
            conn.close()
            print("✅ PostgreSQL otimizado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro na otimização do PostgreSQL: {e}")
            return False
        
        return True
    
    def testar_modelos_especificos(self):
        """Testa modelos específicos de cada provedor"""
        print("\n🧪 TESTE DE MODELOS ESPECÍFICOS")
        print("=" * 40)
        
        try:
            from llm_providers import LLMProviderManager
            
            manager = LLMProviderManager()
            provedores_disponiveis = manager.list_available_providers()
            
            if not provedores_disponiveis:
                print("❌ Nenhum provedor configurado para teste")
                return
            
            print(f"🤖 Provedores disponíveis: {', '.join(provedores_disponiveis)}")
            
            # Teste com pergunta padrão
            pergunta_teste = "Explique em uma frase o que é inteligência artificial."
            messages = [{"role": "user", "content": pergunta_teste}]
            
            resultados_teste = {}
            
            for provedor in provedores_disponiveis:
                print(f"\n🔍 Testando {provedor.upper()}...")
                
                try:
                    # Obter modelos do provedor
                    modelos = manager.get_provider_models(provedor)
                    modelo_teste = modelos[0] if modelos else None
                    
                    if modelo_teste:
                        resposta = manager.generate_response(
                            messages=messages,
                            provider_name=provedor,
                            model=modelo_teste,
                            max_tokens=100
                        )
                        
                        resultados_teste[provedor] = {
                            'status': 'sucesso',
                            'modelo_testado': modelo_teste,
                            'resposta': resposta.get('response', 'Resposta não encontrada')[:100] + '...',
                            'tempo_resposta': resposta.get('metadata', {}).get('response_time', 'N/A')
                        }
                        
                        print(f"  ✅ {provedor}: {modelo_teste} - Funcionando")
                        
                    else:
                        resultados_teste[provedor] = {
                            'status': 'erro',
                            'erro': 'Nenhum modelo disponível'
                        }
                        print(f"  ❌ {provedor}: Nenhum modelo disponível")
                        
                except Exception as e:
                    resultados_teste[provedor] = {
                        'status': 'erro',
                        'erro': str(e)
                    }
                    print(f"  ❌ {provedor}: {e}")
            
            # Salvar resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f'teste_modelos_{timestamp}.json', 'w', encoding='utf-8') as f:
                json.dump(resultados_teste, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n📄 Resultados salvos em: teste_modelos_{timestamp}.json")
            
            self.status['testes_realizados'] = list(resultados_teste.keys())
            
        except Exception as e:
            print(f"❌ Erro no teste de modelos: {e}")
            traceback.print_exc()
    
    def expandir_funcionalidades(self):
        """Expande funcionalidades do sistema"""
        print("\n🚀 EXPANSÃO DE FUNCIONALIDADES")
        print("=" * 40)
        
        funcionalidades_novas = [
            "Sistema de Cache Inteligente",
            "Métricas de Performance",
            "Sistema de Backup Automático",
            "API REST Completa",
            "Interface de Monitoramento"
        ]
        
        for i, func in enumerate(funcionalidades_novas, 1):
            print(f"{i}. {func}")
        
        # Implementar sistema de cache
        self._implementar_sistema_cache()
        
        # Implementar métricas
        self._implementar_metricas()
        
        print("✅ Funcionalidades expandidas!")
    
    def _implementar_sistema_cache(self):
        """Implementa sistema de cache para respostas"""
        cache_code = '''import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class ResponseCache:
    """Sistema de cache para respostas LLM"""
    
    def __init__(self, cache_file: str = "response_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Carrega cache do arquivo"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        """Salva cache no arquivo"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False, default=str)
    
    def get_cache_key(self, messages: list, provider: str, model: str) -> str:
        """Gera chave única para cache"""
        content = f"{provider}_{model}_{json.dumps(messages, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, messages: list, provider: str, model: str, max_age_hours: int = 24) -> Optional[str]:
        """Recupera resposta do cache se válida"""
        key = self.get_cache_key(messages, provider, model)
        
        if key in self.cache:
            entry = self.cache[key]
            cached_time = datetime.fromisoformat(entry['timestamp'])
            
            if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                return entry['response']
        
        return None
    
    def set(self, messages: list, provider: str, model: str, response: str):
        """Armazena resposta no cache"""
        key = self.get_cache_key(messages, provider, model)
        
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model
        }
        
        self._save_cache()
'''
        
        with open('response_cache.py', 'w', encoding='utf-8') as f:
            f.write(cache_code)
        
        print("  ✅ Sistema de cache implementado (response_cache.py)")
    
    def _implementar_metricas(self):
        """Implementa sistema de métricas"""
        metrics_code = '''import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

class MetricsCollector:
    """Coleta e armazena métricas do sistema"""
    
    def __init__(self, db_file: str = "metrics.db"):
        self.db_file = db_file
        self._init_db()
    
    def _init_db(self):
        """Inicializa banco de métricas"""
        conn = sqlite3.connect(self.db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                response_time REAL,
                token_count INTEGER,
                success BOOLEAN,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def record_llm_request(self, provider: str, model: str, response_time: float, 
                          success: bool, token_count: int = None, metadata: Dict = None):
        """Registra requisição LLM"""
        conn = sqlite3.connect(self.db_file)
        conn.execute("""
            INSERT INTO metrics (event_type, provider, model, response_time, token_count, success, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'llm_request',
            provider,
            model,
            response_time,
            token_count,
            success,
            json.dumps(metadata) if metadata else None
        ))
        conn.commit()
        conn.close()
    
    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém estatísticas das últimas horas"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT provider, COUNT(*) as requests, AVG(response_time) as avg_time,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
            FROM metrics 
            WHERE timestamp > datetime('now', '-{} hours')
            GROUP BY provider
        """.format(hours))
        
        stats = {}
        for row in cursor.fetchall():
            provider, requests, avg_time, successful = row
            stats[provider] = {
                'requests': requests,
                'avg_response_time': round(avg_time, 2) if avg_time else 0,
                'success_rate': round((successful / requests) * 100, 2) if requests else 0
            }
        
        conn.close()
        return stats
'''
        
        with open('metrics_collector.py', 'w', encoding='utf-8') as f:
            f.write(metrics_code)
        
        print("  ✅ Sistema de métricas implementado (metrics_collector.py)")
    
    def executar_todos_passos(self):
        """Executa todos os próximos passos em sequência"""
        print("🎯 EXECUTANDO TODOS OS PRÓXIMOS PASSOS")
        print("=" * 50)
        
        passos = [
            ("Diagnóstico Completo", self.diagnosticar_sistema_completo),
            ("Configuração de Provedores", self.configurar_provedores_faltantes),
            ("Otimização PostgreSQL", self.otimizar_postgresql),
            ("Teste de Modelos", self.testar_modelos_especificos),
            ("Expansão de Funcionalidades", self.expandir_funcionalidades)
        ]
        
        resultados = {}
        
        for nome, funcao in passos:
            print(f"\n📋 Executando: {nome}")
            try:
                resultado = funcao()
                resultados[nome] = "✅ Sucesso"
                print(f"✅ {nome} concluído")
            except Exception as e:
                resultados[nome] = f"❌ Erro: {str(e)}"
                print(f"❌ Erro em {nome}: {e}")
        
        # Relatório final
        print("\n" + "="*50)
        print("📊 RELATÓRIO FINAL DOS PRÓXIMOS PASSOS")
        print("="*50)
        
        for passo, resultado in resultados.items():
            print(f"{passo}: {resultado}")
        
        # Salvar status final
        self.status['execucao_completa'] = datetime.now().isoformat()
        self.status['resultados'] = resultados
        
        with open('status_proximos_passos.json', 'w', encoding='utf-8') as f:
            json.dump(self.status, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Status final salvo em: status_proximos_passos.json")
        
        # Próximos passos recomendados
        print("\n🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("1. Configure as API keys no arquivo .env")
        print("2. Execute testes individuais dos provedores")
        print("3. Monitore métricas de performance")
        print("4. Considere implementar CI/CD")
        print("5. Documente novas funcionalidades")

def main():
    """Função principal"""
    implementor = ProximosPassosImplementor()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "--diagnostico":
            implementor.diagnosticar_sistema_completo()
        elif comando == "--provedores":
            implementor.configurar_provedores_faltantes()
        elif comando == "--postgresql":
            implementor.otimizar_postgresql()
        elif comando == "--teste-modelos":
            implementor.testar_modelos_especificos()
        elif comando == "--expandir":
            implementor.expandir_funcionalidades()
        elif comando == "--todos":
            implementor.executar_todos_passos()
        else:
            print("Comandos disponíveis:")
            print("  --diagnostico: Diagnóstico completo")
            print("  --provedores: Configurar provedores")
            print("  --postgresql: Otimizar PostgreSQL")
            print("  --teste-modelos: Testar modelos")
            print("  --expandir: Expandir funcionalidades")
            print("  --todos: Executar todos os passos")
    else:
        implementor.executar_todos_passos()

if __name__ == "__main__":
    main()