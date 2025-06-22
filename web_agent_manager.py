import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, g
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path

# Adiar a importação de Agent e Database
# from agent_system import Agent
# from database import Database
from llm_providers import llm_manager
# from extension_api import extension_api_bp

# Configuração
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'agent_uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

# Importa e registra o blueprint e inicializa o banco de dados
from database import Database
from extension_api import extension_api_bp
from agent_system import Agent
from scraper import scrape_url # Importa a nova função

Database.initialize_pool()
app.register_blueprint(extension_api_bp)

@app.context_processor
def inject_agent_class():
    """Disponibiliza a classe Agent para os contextos de requisição."""
    return {'Agent': Agent}

# Usar o contexto da aplicação para o 'g'
@app.before_request
def before_request_func():
    g.Agent = Agent

# --- Rotas da Interface (HTML) ---
@app.route('/')
def home():
    return redirect(url_for('agent_dashboard'))

@app.route('/agents')
def agent_dashboard():
    agents = Agent.get_all()
    stats_list = {agent.id: agent.get_stats() for agent in agents}
    return render_template('agents.html', agents=agents, stats=stats_list)

@app.route('/agents/<agent_id>')
def agent_detail_page(agent_id):
    agent = Agent.get_by_id(agent_id)
    if not agent:
        return "Agente não encontrado", 404
    stats = agent.get_stats()
    available_providers = llm_manager.list_available_providers()
    return render_template('agent_detail.html', agent=agent, stats=stats, providers=available_providers)

# --- Rotas da API (JSON) ---

@app.route('/api/v1/agents', methods=['GET', 'POST'])
def handle_agents():
    if request.method == 'GET':
        agents = Agent.get_all()
        return jsonify([agent.to_dict() for agent in agents])
    
    if request.method == 'POST':
        data = request.json
        agent = Agent.create(data)
        if agent:
            return jsonify(agent.to_dict()), 201
        return jsonify({"error": "Falha ao criar agente"}), 500

@app.route('/api/v1/agents/<agent_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_agent_detail(agent_id):
    agent = Agent.get_by_id(agent_id)
    if not agent:
        return jsonify({"error": "Agente não encontrado"}), 404
        
    if request.method == 'GET':
        stats = agent.get_stats()
        return jsonify({"agent": agent.to_dict(), "stats": stats})
        
    if request.method == 'PUT':
        data = request.json
        updated_agent = Agent.update(agent_id, data)
        if updated_agent:
            return jsonify(updated_agent.to_dict())
        return jsonify({"error": "Falha ao atualizar agente"}), 500
        
    if request.method == 'DELETE':
        Agent.delete(agent_id)
        return jsonify({"success": True}), 200

@app.route('/api/v1/agents/<agent_id>/chat', methods=['POST'])
def handle_chat(agent_id):
    agent = Agent.get_by_id(agent_id)
    if not agent: return jsonify({"error": "Agente não encontrado"}), 404
        
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    compare_llms = data.get('compare_llms', False)
    providers = data.get('providers', ['openai'])

    if not user_message: return jsonify({"error": "Mensagem não pode ser vazia"}), 400

    conversation_id = agent.save_conversation(user_message)
    if not conversation_id: return jsonify({"error": "Falha ao salvar conversa"}), 500

    if compare_llms:
        multi_response = agent.get_multi_llm_response(user_message, history, providers)
        responses_saved = []
        for provider, resp_data in multi_response.items():
            resp_id = agent.save_llm_response(conversation_id, provider, resp_data.get('model', 'N/A'), resp_data.get('content', ''), resp_data.get('usage', {}).get('total_tokens', 0))
            responses_saved.append({'id': resp_id, 'provider': provider, 'content': resp_data.get('content', '')})
        return jsonify({"id": conversation_id, "role": "assistant", "responses": responses_saved})
    else:
        # Garante que o modelo não seja vazio
        model_to_use = agent.model if agent.model and agent.model.strip() else "gpt-4o-mini"
        response_text = agent.get_response(user_message, history)
        response_id = agent.save_llm_response(conversation_id, agent.llm_provider_name, model_to_use, response_text, 0)
        return jsonify({"id": response_id, "role": "assistant", "content": response_text})

@app.route('/api/v1/agents/<agent_id>/history', methods=['GET'])
def get_history(agent_id):
    agent = Agent.get_by_id(agent_id)
    if not agent: return jsonify({"error": "Agente não encontrado"}), 404
    history = agent.get_full_history()
    return jsonify(history)

@app.route('/api/v1/responses/<response_id>/feedback', methods=['POST'])
def handle_feedback(response_id):
    data = request.json
    feedback = data.get('feedback')
    if feedback not in [1, -1]: return jsonify({"error": "Feedback inválido"}), 400
    
    success = Agent.set_feedback(response_id, feedback)
    if success: return jsonify({"success": True})
    return jsonify({"error": "Falha ao registrar feedback"}), 500

@app.route('/api/v1/capture_page', methods=['POST'])
def handle_capture_page():
    """
    Endpoint para capturar o conteúdo de uma URL, processá-lo e adicioná-lo
    à base de conhecimento de um agente.
    """
    data = request.json
    agent_id = data.get('agent_id')
    url = data.get('url')

    if not all([agent_id, url]):
        return jsonify({"error": "Dados incompletos: agent_id e url são obrigatórios."}), 400

    agent = Agent.get_by_id(agent_id)
    if not agent:
        return jsonify({"error": "Agente não encontrado"}), 404
    
    # Inicia o processo de scraping em segundo plano para não travar a API
    logging.info(f"Iniciando captura da URL '{url}' para o agente '{agent.name}'.")
    
    scrape_result = scrape_url(url)
    
    if not scrape_result.get("success"):
        return jsonify({"error": f"Falha ao capturar conteúdo da URL: {scrape_result.get('error')}"}), 500

    try:
        # Usa o conteúdo capturado para adicionar ao agente
        content = scrape_result.get("content")
        title = scrape_result.get("title")
        document_source = f"{title} ({url})" # Cria uma fonte descritiva

        agent.add_document_from_text(content, document_source)
        
        logging.info(f"Conteúdo de '{url}' adicionado com sucesso ao agente '{agent.name}'.")
        return jsonify({
            "success": True, 
            "message": f"Conteúdo da página '{title}' adicionado ao agente '{agent.name}'."
        })
    except Exception as e:
        logging.error(f"Erro ao adicionar documento de URL para o agente {agent_id}: {e}", exc_info=True)
        return jsonify({"error": "Falha ao salvar o conteúdo capturado na base de conhecimento."}), 500

@app.route('/add_document', methods=['POST'])
def add_document_from_extension():
    """Endpoint para a extensão do Chrome salvar conteúdo de uma página."""
    data = request.json
    agent_id = data.get('agent_id')
    content = data.get('content')
    source = data.get('source')

    if not all([agent_id, content, source]):
        return jsonify({"error": "Dados incompletos: agent_id, content e source são obrigatórios."}), 400

    agent = Agent.get_by_id(agent_id)
    if not agent:
        return jsonify({"error": "Agente não encontrado"}), 404

    try:
        agent.add_document_from_text(content, source)
        return jsonify({"success": True, "message": f"Conteúdo da fonte '{source}' adicionado ao agente '{agent.name}'."})
    except Exception as e:
        logging.error(f"Erro ao adicionar documento via extensão: {e}")
        return jsonify({"error": "Falha ao processar e adicionar o documento."}), 500

@app.route('/api/v1/agents/<agent_id>/upload', methods=['POST'])
def handle_upload(agent_id):
    try:
        logging.info(f"🔍 Iniciando upload para agente {agent_id}")
        
        agent = Agent.get_by_id(agent_id)
        if not agent: 
            logging.error(f"❌ Agente {agent_id} não encontrado")
            return jsonify({"error": "Agente não encontrado"}), 404
        
        logging.info(f"✅ Agente encontrado: {agent.name}")
        
        if 'file' not in request.files: 
            logging.error("❌ Nenhum arquivo na requisição")
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        file = request.files['file']
        if file.filename == '': 
            logging.error("❌ Nome de arquivo vazio")
            return jsonify({"error": "Nome de arquivo vazio"}), 400
            
        if file:
            filename = secure_filename(file.filename)
            agent_upload_dir = Path(app.config['UPLOAD_FOLDER']) / agent_id
            agent_upload_dir.mkdir(exist_ok=True)
            file_path = agent_upload_dir / filename
            
            logging.info(f"💾 Salvando arquivo: {file_path}")
            
            # Salva o arquivo
            file.save(file_path)
            
            # Verifica se o arquivo foi salvo
            if file_path.exists():
                logging.info(f"✅ Arquivo salvo com sucesso: {file_path} ({file_path.stat().st_size} bytes)")
            else:
                logging.error(f"❌ Arquivo não foi salvo: {file_path}")
                return jsonify({"error": "Falha ao salvar arquivo"}), 500
            
            logging.info(f"🤖 Adicionando documento ao sistema RAG do agente")
            
            # Adiciona ao sistema RAG
            agent.add_document(str(file_path))
            
            logging.info(f"✅ Upload concluído com sucesso para {filename}")
            
            return jsonify({
                "success": True, 
                "message": f"Arquivo '{filename}' adicionado com sucesso ao agente."
            })
    except Exception as e:
        logging.error(f"❌ Erro no upload: {e}", exc_info=True)
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/v1/models', methods=['GET'])
def get_available_models():
    """Retorna lista de modelos disponíveis para seleção"""
    common_models = [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "llama-3.1-70b-instruct",
        "llama-3.1-8b-instruct"
    ]
    
    return jsonify({
        "common_models": common_models,
        "active_provider": llm_manager.active_provider,
        "available_providers": llm_manager.list_available_providers()
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0') 