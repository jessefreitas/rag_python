import logging
import tempfile
import os
from flask import Blueprint, request, jsonify, g
from pathlib import Path

# Adiar a importação do Agent para evitar importação circular
# from agent_system import Agent 

extension_api_bp = Blueprint('extension_api', __name__, url_prefix='/api/v1/extension')

logging.basicConfig(level=logging.INFO)

@extension_api_bp.route('/save_content', methods=['POST'])
def save_content():
    """
    Recebe conteúdo de uma página web da extensão do Chrome e o salva
    como um documento para um agente específico.
    """
    Agent = g.Agent # Acessa a classe Agent a partir do contexto global da aplicação
    data = request.json
    
    agent_id = data.get('agent_id')
    url = data.get('url')
    title = data.get('title')
    content = data.get('content')

    if not all([agent_id, url, title, content]):
        return jsonify({"error": "Dados incompletos: agent_id, url, title e content são obrigatórios."}), 400

    agent = Agent.get_by_id(agent_id)
    if not agent:
        return jsonify({"error": "Agente não encontrado"}), 404

    try:
        # Cria um arquivo de texto temporário para o RAGSystem processar
        # O nome do arquivo será baseado no título da página
        safe_filename = "".join([c for c in title if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()
        
        # Garante que a pasta de uploads do agente exista
        agent_upload_dir = Path(os.environ.get('UPLOAD_FOLDER', 'agent_uploads')) / agent_id
        agent_upload_dir.mkdir(exist_ok=True)
        
        file_path = agent_upload_dir / f"{safe_filename}.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Source URL: {url}\n\n")
            f.write(f"Page Title: {title}\n\n")
            f.write("="*20 + " CONTENT " + "="*20 + "\n\n")
            f.write(content)

        # Adiciona o arquivo de texto como um documento para o agente
        agent.add_document(str(file_path))
        
        logging.info(f"Conteúdo da URL '{url}' salvo com sucesso para o agente '{agent.name}' (ID: {agent_id})")
        return jsonify({"success": True, "message": f"Conteúdo salvo no agente '{agent.name}'."}), 201

    except Exception as e:
        logging.error(f"Falha ao salvar conteúdo da extensão: {e}")
        return jsonify({"error": f"Erro interno no servidor: {e}"}), 500 