#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Server para Extensão Chrome - Conexão REAL com Supabase
"""

import os
import sys
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verificar se extension_api existe
try:
    from extension_api import extension_api
    print("✅ extension_api importado com sucesso")
except ImportError as e:
    print(f"⚠️ extension_api não encontrado: {e}")
    extension_api = None

app = Flask(__name__)
CORS(app)

# Configurações do Supabase
SUPABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'db.fwzztbgmzxruqmtmafhe.supabase.co'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '30291614')
}

def get_db_connection():
    """Conecta ao Supabase PostgreSQL"""
    try:
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase: {e}")
        return None

def get_real_agents():
    """Busca agentes reais do Supabase"""
    conn = get_db_connection()
    if not conn:
        logger.error("❌ Sem conexão com Supabase")
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Buscar agentes da tabela agents
            cursor.execute("""
                SELECT 
                    id,
                    name,
                    description,
                    created_at,
                    (SELECT COUNT(*) FROM documents WHERE agent_id = agents.id) as document_count
                FROM agents 
                ORDER BY created_at DESC
            """)
            
            agents = cursor.fetchall()
            
            # Converter para formato da extensão
            formatted_agents = []
            for agent in agents:
                formatted_agents.append({
                    'id': str(agent['id']),
                    'name': agent['name'],
                    'description': agent['description'] or f"Agente {agent['name']}",
                    'document_count': agent['document_count'],
                    'created_at': agent['created_at'].isoformat() if agent['created_at'] else None
                })
            
            logger.info(f"✅ {len(formatted_agents)} agentes encontrados no Supabase")
            return formatted_agents
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar agentes: {e}")
        return []
    finally:
        conn.close()

def save_scraped_content(agent_id, url, title, content):
    """Salva conteúdo raspado no Supabase"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            # Inserir documento na tabela documents
            cursor.execute("""
                INSERT INTO documents (id, agent_id, filename, content, metadata, created_at)
                VALUES (gen_random_uuid(), %s, %s, %s, %s, NOW())
                RETURNING id
            """, (
                agent_id,
                f"scraped_{title[:50]}.txt",
                content,
                json.dumps({
                    'source': 'chrome_extension',
                    'url': url,
                    'title': title,
                    'type': 'scraped_content'
                })
            ))
            
            doc_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"✅ Conteúdo salvo: {doc_id}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao salvar conteúdo: {e}")
        return False
    finally:
        conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check com verificação de Supabase"""
    # Testar conexão com Supabase
    conn = get_db_connection()
    supabase_status = "connected" if conn else "disconnected"
    if conn:
        conn.close()
    
    return jsonify({
        'status': 'ok',
        'message': 'RAG Python API funcionando',
        'supabase': supabase_status,
        'endpoints': ['/api/health', '/api/agents', '/api/stats', '/api/process']
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Busca agentes reais do Supabase"""
    try:
        agents = get_real_agents()
        
        if not agents:
            # Fallback se não houver agentes
            agents = [{
                'id': 'default',
                'name': 'Agente Padrão',
                'description': 'Agente criado automaticamente',
                'document_count': 0,
                'created_at': None
            }]
        
        return jsonify({
            'success': True,
            'agents': agents,
            'total': len(agents),
            'source': 'supabase'
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar agentes: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'agents': [],
            'source': 'error'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Estatísticas reais do Supabase"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'success': False,
            'error': 'Sem conexão com Supabase'
        }), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Contar agentes
            cursor.execute("SELECT COUNT(*) as count FROM agents")
            agents_count = cursor.fetchone()['count']
            
            # Contar documentos
            cursor.execute("SELECT COUNT(*) as count FROM documents")
            docs_count = cursor.fetchone()['count']
            
            # Documentos por agente
            cursor.execute("""
                SELECT a.name, COUNT(d.id) as doc_count
                FROM agents a
                LEFT JOIN documents d ON a.id = d.agent_id
                GROUP BY a.id, a.name
                ORDER BY doc_count DESC
            """)
            agents_stats = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_agents': agents_count,
                'total_documents': docs_count,
                'agents_breakdown': [dict(row) for row in agents_stats]
            },
            'source': 'supabase'
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        conn.close()

@app.route('/api/process', methods=['POST'])
def process_content():
    """Processa conteúdo raspado e salva no Supabase"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        agent_id = data.get('agent_id')
        url = data.get('url')
        title = data.get('title', 'Página sem título')
        content = data.get('content', '')
        
        if not agent_id or not content:
            return jsonify({
                'success': False,
                'error': 'agent_id e content são obrigatórios'
            }), 400
        
        # Salvar no Supabase
        success = save_scraped_content(agent_id, url, title, content)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conteúdo processado e salvo com sucesso',
                'agent_id': agent_id,
                'url': url,
                'content_length': len(content)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Falha ao salvar no Supabase'
            }), 500
            
    except Exception as e:
        logger.error(f"Erro ao processar conteúdo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api', methods=['GET'])
def api_info():
    """Informações da API"""
    return jsonify({
        'name': 'RAG Python Extension API',
        'version': '1.5.1',
        'description': 'API para extensão Chrome com conexão real ao Supabase',
        'supabase_host': SUPABASE_CONFIG['host'],
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/agents': 'Lista agentes do Supabase',
            'GET /api/stats': 'Estatísticas do sistema',
            'POST /api/process': 'Processa conteúdo raspado'
        }
    })

if __name__ == '__main__':
    print("🚀 RAG Python - Servidor de API para Extensão")
    print("=" * 50)
    print("🔌 Iniciando servidor de API para extensão Chrome...")
    print("📡 URL: http://localhost:5000")
    print("🔗 Endpoints disponíveis:")
    print("   - GET  /api/health")
    print("   - GET  /api/agents")
    print("   - GET  /api/stats")
    print("   - POST /api/process")
    print("   - GET  /api (info)")
    print("🗄️ Conectando ao Supabase:")
    print(f"   - Host: {SUPABASE_CONFIG['host']}")
    print(f"   - Database: {SUPABASE_CONFIG['database']}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False) 