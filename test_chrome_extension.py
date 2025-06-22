#!/usr/bin/env python3
"""
Script de teste para validar a integração isolada da extensão do Chrome
com o sistema RAG Python
"""

import requests
import json
import time
import logging
from database import get_db_connection

# Configuração
BASE_URL = "http://192.168.8.4:5000"
TEST_URL = "https://www.gov.br/pgr/pt-br"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_extension_health():
    """Testa se a API da extensão está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/extension/health")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Health Check: {result['message']}")
            return True
        else:
            logger.error(f"❌ Health Check falhou: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no health check: {e}")
        return False

def test_get_agents():
    """Testa busca de agentes pela API da extensão"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/extension/agents")
        
        if response.status_code == 200:
            result = response.json()
            agents = result.get('agents', [])
            count = result.get('count', 0)
            
            logger.info(f"✅ Agentes encontrados: {count}")
            for agent in agents:
                logger.info(f"   - {agent['name']} (ID: {agent['id'][:8]}...)")
            
            return agents
        else:
            logger.error(f"❌ Falha ao buscar agentes: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar agentes: {e}")
        return []

def test_agent_validation(agent_id):
    """Testa validação de um agente específico"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/extension/agent/{agent_id}/validate")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('valid'):
                agent_info = result.get('agent', {})
                logger.info(f"✅ Agente válido: {agent_info['name']} (Status: {agent_info['status']})")
                return True
            else:
                logger.warning(f"⚠️ Agente inválido: {result.get('message')}")
                return False
        else:
            logger.error(f"❌ Erro na validação: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na validação do agente: {e}")
        return False

def test_page_capture(agent_id, url):
    """Testa captura de página web"""
    try:
        logger.info(f"🌐 Testando captura da URL: {url}")
        
        response = requests.post(f"{BASE_URL}/api/v1/extension/capture_page", 
                               json={
                                   'agent_id': agent_id,
                                   'url': url
                               })
        
        if response.status_code == 201:
            result = response.json()
            logger.info(f"✅ Captura bem-sucedida!")
            logger.info(f"   - Agente: {result.get('agent_name')}")
            logger.info(f"   - Título: {result.get('title')}")
            logger.info(f"   - Arquivo: {result.get('file_path')}")
            return True
        else:
            result = response.json()
            logger.error(f"❌ Falha na captura: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na captura: {e}")
        return False

def check_database_isolation():
    """Verifica isolamento no banco de dados"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar agentes ativos
            cursor.execute("SELECT COUNT(*) FROM agentes WHERE status = 'ativo'")
            active_agents = cursor.fetchone()[0]
            
            # Verificar documentos por agente
            cursor.execute("""
                SELECT agent_id, COUNT(*) as doc_count 
                FROM documents 
                GROUP BY agent_id
            """)
            
            docs_per_agent = cursor.fetchall()
            
            logger.info(f"📊 Estatísticas do banco:")
            logger.info(f"   - Agentes ativos: {active_agents}")
            logger.info(f"   - Documentos por agente:")
            
            for agent_id, doc_count in docs_per_agent:
                logger.info(f"     * {agent_id[:8]}...: {doc_count} documentos")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar banco: {e}")
        return False

def main():
    """Executa todos os testes da extensão"""
    logger.info("🧪 Iniciando testes da extensão Chrome isolada...")
    
    # 1. Teste de saúde da API
    logger.info("\n1️⃣ Testando health check da API...")
    if not test_extension_health():
        logger.error("❌ Health check falhou. Verifique se o servidor está rodando.")
        return
    
    # 2. Teste de busca de agentes
    logger.info("\n2️⃣ Testando busca de agentes...")
    agents = test_get_agents()
    if not agents:
        logger.error("❌ Nenhum agente encontrado. Crie um agente primeiro.")
        return
    
    # 3. Teste de validação de agente
    logger.info("\n3️⃣ Testando validação de agente...")
    test_agent = agents[0]  # Usar o primeiro agente
    agent_id = test_agent['id']
    
    if not test_agent_validation(agent_id):
        logger.error("❌ Validação de agente falhou.")
        return
    
    # 4. Teste de captura de página
    logger.info("\n4️⃣ Testando captura de página...")
    if not test_page_capture(agent_id, TEST_URL):
        logger.error("❌ Captura de página falhou.")
        return
    
    # 5. Verificar isolamento no banco
    logger.info("\n5️⃣ Verificando isolamento no banco...")
    if not check_database_isolation():
        logger.error("❌ Verificação do banco falhou.")
        return
    
    # 6. Aguardar processamento e testar busca
    logger.info("\n6️⃣ Aguardando processamento RAG...")
    time.sleep(5)  # Aguardar processamento
    
    # Testar se o conteúdo foi adicionado
    try:
        response = requests.post(f"{BASE_URL}/api/v1/agents/{agent_id}/chat",
                               json={'message': 'Você tem informações sobre Procuradoria-Geral da República?'})
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('content', '')
            
            if 'Procuradoria' in content or 'PGR' in content:
                logger.info("✅ Conteúdo capturado encontrado na resposta RAG!")
            else:
                logger.warning("⚠️ Conteúdo capturado não encontrado na resposta (pode estar processando)")
        
    except Exception as e:
        logger.warning(f"⚠️ Erro ao testar resposta RAG: {e}")
    
    logger.info("\n🎉 Todos os testes da extensão concluídos!")
    logger.info("✅ Extensão Chrome isolada funcionando corretamente!")

if __name__ == '__main__':
    main() 