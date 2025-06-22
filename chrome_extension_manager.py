"""
Sistema isolado para gerenciamento da extensão do Chrome
"""

import logging
from flask import Blueprint, request, jsonify
from agent_system import Agent
from scraper import scrape_url

logger = logging.getLogger(__name__)

# Blueprint para isolamento da extensão
chrome_extension_bp = Blueprint('chrome_extension', __name__, url_prefix='/api/v1/extension')

class ChromeExtensionManager:
    """Gerenciador isolado para a extensão do Chrome"""
    
    def get_agents_from_db(self):
        """Busca todos os agentes ativos do banco de dados"""
        try:
            agents = Agent.get_all()
            agent_list = []
            for agent in agents:
                agent_list.append({
                    'id': agent.id,
                    'name': agent.name,
                    'description': agent.description,
                    'status': 'ativo'
                })
            
            logger.info(f"🔍 ChromeExtension: Encontrados {len(agent_list)} agentes ativos")
            return agent_list
            
        except Exception as e:
            logger.error(f"❌ ChromeExtension: Erro ao buscar agentes: {e}")
            return []
    
    def process_url_content(self, agent_id: str, url: str):
        """Processa conteúdo de uma URL para um agente específico"""
        try:
            # 1. Validar agente
            agent = Agent.get_by_id(agent_id)
            if not agent:
                raise ValueError(f"Agente {agent_id} não encontrado")
            
            logger.info(f"🌐 ChromeExtension: Iniciando captura de {url} para agente {agent.name}")
            
            # 2. Fazer scraping da URL
            scrape_result = scrape_url(url)
            if not scrape_result.get('success'):
                raise ValueError(f"Erro no scraping: {scrape_result.get('error')}")
            
            # 3. Usar método do agente para adicionar conteúdo
            title = scrape_result.get('title', 'Página sem título')
            content = scrape_result.get('content', '')
            document_source = f"{title} ({url})"
            
            # 4. Adicionar documento ao agente
            agent.add_document_from_text(content, document_source)
            
            logger.info(f"✅ ChromeExtension: Conteúdo de {url} processado com sucesso para agente {agent.name}")
            
            return {
                'success': True,
                'message': f"Conteúdo capturado e adicionado ao agente '{agent.name}'",
                'agent_name': agent.name,
                'url': url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"❌ ChromeExtension: Erro ao processar URL {url}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Instância global do gerenciador
extension_manager = ChromeExtensionManager()

# ====== ROTAS DA API ======

@chrome_extension_bp.route('/agents', methods=['GET'])
def get_agents():
    """Retorna lista de agentes disponíveis para a extensão"""
    try:
        agents = extension_manager.get_agents_from_db()
        return jsonify({
            'success': True,
            'agents': agents,
            'count': len(agents)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ ChromeExtension API: Erro ao buscar agentes: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@chrome_extension_bp.route('/capture_page', methods=['POST'])
def capture_page():
    """Captura conteúdo de uma página web para um agente"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        url = data.get('url')
        
        # Validações
        if not agent_id or not url:
            return jsonify({
                'success': False,
                'error': 'agent_id e url são obrigatórios'
            }), 400
        
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': 'URL deve começar com http:// ou https://'
            }), 400
        
        # Processar conteúdo
        result = extension_manager.process_url_content(agent_id, url)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"❌ ChromeExtension API: Erro na captura: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@chrome_extension_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica se a API da extensão está funcionando"""
    try:
        # Teste básico de conectividade
        agents = Agent.get_all()
        return jsonify({
            'success': True,
            'status': 'healthy',
            'agents_count': len(agents)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ ChromeExtension Health: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

def register_extension_api(app):
    """Registra a API da extensão no Flask app"""
    app.register_blueprint(chrome_extension_bp)
    logger.info("✅ API da extensão Chrome registrada")

def test_extension_integration():
    """Testa a integração da extensão"""
    try:
        agents = Agent.get_all()
        logger.info(f"✅ Teste de integração: {len(agents)} agentes encontrados")
        return True
    except Exception as e:
        logger.error(f"❌ Teste de integração falhou: {e}")
        return False 