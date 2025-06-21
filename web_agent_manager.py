"""
Sistema Web para Gerenciamento de Agentes RAG
Permite upload de arquivos para pastas específicas de agentes e criação de agentes personalizados
"""

import os
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import zipfile

from agent_system import AgentConfig, BaseAgent, MultiAgentSystem
from rag_system import RAGSystem
from vector_store import VectorStore
from document_loader import load_document, get_text_splitter

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
CORS(app)

# Configurações
UPLOAD_FOLDER = 'agent_uploads'
AGENTS_CONFIG_FILE = 'agents_config.json'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'doc', 'pptx', 'xlsx'}

# Criar pastas necessárias
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path('agent_vector_dbs').mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentManager:
    """Gerenciador de agentes e seus documentos"""
    
    def __init__(self):
        self.agents_config_file = AGENTS_CONFIG_FILE
        self.agents = {}
        self.load_agents_config()
    
    def load_agents_config(self):
        """Carrega configuração dos agentes do arquivo JSON"""
        try:
            if os.path.exists(self.agents_config_file):
                with open(self.agents_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.agents = config.get('agents', {})
                logger.info(f"Configuração carregada: {len(self.agents)} agentes")
            else:
                self.agents = {}
                self.save_agents_config()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self.agents = {}
    
    def save_agents_config(self):
        """Salva configuração dos agentes no arquivo JSON"""
        try:
            config = {
                'agents': self.agents,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.agents_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info("Configuração salva com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """Cria um novo agente"""
        try:
            agent_id = str(uuid.uuid4())
            
            # Criar estrutura de pastas
            agent_folder = Path(UPLOAD_FOLDER) / agent_id
            agent_folder.mkdir(parents=True, exist_ok=True)
            
            # Criar pasta para banco de vetores
            vector_db_folder = Path('agent_vector_dbs') / agent_id
            vector_db_folder.mkdir(parents=True, exist_ok=True)
            
            # Configuração do agente
            agent_config = {
                'id': agent_id,
                'name': agent_data['name'],
                'description': agent_data['description'],
                'system_prompt': agent_data['system_prompt'],
                'model_name': agent_data.get('model_name', 'gpt-3.5-turbo'),
                'temperature': agent_data.get('temperature', 0.7),
                'max_iterations': agent_data.get('max_iterations', 5),
                'memory': agent_data.get('memory', True),
                'tools': agent_data.get('tools', ['rag_query', 'search_documents']),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'document_count': 0,
                'folder_path': str(agent_folder),
                'vector_db_path': str(vector_db_folder)
            }
            
            self.agents[agent_id] = agent_config
            self.save_agents_config()
            
            logger.info(f"Agente criado: {agent_data['name']} (ID: {agent_id})")
            return agent_id
            
        except Exception as e:
            logger.error(f"Erro ao criar agente: {e}")
            raise
    
    def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """Atualiza um agente existente"""
        try:
            if agent_id not in self.agents:
                return False
            
            # Atualizar campos permitidos
            allowed_fields = ['name', 'description', 'system_prompt', 'model_name', 
                            'temperature', 'max_iterations', 'memory', 'tools']
            
            for field in allowed_fields:
                if field in agent_data:
                    self.agents[agent_id][field] = agent_data[field]
            
            self.agents[agent_id]['updated_at'] = datetime.now().isoformat()
            self.save_agents_config()
            
            logger.info(f"Agente atualizado: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar agente: {e}")
            return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """Deleta um agente e seus arquivos"""
        try:
            if agent_id not in self.agents:
                return False
            
            # Remover pastas
            agent_folder = Path(self.agents[agent_id]['folder_path'])
            vector_db_folder = Path(self.agents[agent_id]['vector_db_path'])
            
            if agent_folder.exists():
                shutil.rmtree(agent_folder)
            
            if vector_db_folder.exists():
                shutil.rmtree(vector_db_folder)
            
            # Remover da configuração
            del self.agents[agent_id]
            self.save_agents_config()
            
            logger.info(f"Agente deletado: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar agente: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um agente"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Obtém lista de todos os agentes"""
        return list(self.agents.values())
    
    def upload_files_to_agent(self, agent_id: str, files: List) -> Dict[str, Any]:
        """Faz upload de arquivos para um agente específico"""
        try:
            if agent_id not in self.agents:
                return {'success': False, 'error': 'Agente não encontrado'}
            
            agent_folder = Path(self.agents[agent_id]['folder_path'])
            uploaded_files = []
            errors = []
            
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    if self.allowed_file(filename):
                        file_path = agent_folder / filename
                        file.save(str(file_path))
                        uploaded_files.append(filename)
                        logger.info(f"Arquivo salvo: {file_path}")
                    else:
                        errors.append(f"Tipo de arquivo não permitido: {filename}")
            
            # Atualizar contagem de documentos
            if uploaded_files:
                self.agents[agent_id]['document_count'] = len(list(agent_folder.glob('*')))
                self.agents[agent_id]['updated_at'] = datetime.now().isoformat()
                self.save_agents_config()
            
            return {
                'success': True,
                'uploaded_files': uploaded_files,
                'errors': errors,
                'total_files': len(uploaded_files)
            }
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_agent_files(self, agent_id: str) -> List[str]:
        """Obtém lista de arquivos de um agente"""
        try:
            if agent_id not in self.agents:
                return []
            
            agent_folder = Path(self.agents[agent_id]['folder_path'])
            if not agent_folder.exists():
                return []
            
            files = []
            for file_path in agent_folder.glob('*'):
                if file_path.is_file():
                    files.append({
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            return []
    
    def delete_agent_file(self, agent_id: str, filename: str) -> bool:
        """Deleta um arquivo específico de um agente"""
        try:
            if agent_id not in self.agents:
                return False
            
            agent_folder = Path(self.agents[agent_id]['folder_path'])
            file_path = agent_folder / filename
            
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                self.agents[agent_id]['document_count'] = len(list(agent_folder.glob('*')))
                self.agents[agent_id]['updated_at'] = datetime.now().isoformat()
                self.save_agents_config()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            return False

    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def query_agent(self, agent_id: str, question: str) -> Dict[str, Any]:
        """Consulta um agente com uma pergunta"""
        try:
            if agent_id not in self.agents:
                return {'success': False, 'error': 'Agente não encontrado'}
            
            agent_config = self.agents[agent_id]
            vector_db_path = agent_config['vector_db_path']
            
            # Inicializar o RAG System específico para o agente
            rag_system = RAGSystem(vector_db_path=vector_db_path)
            
            # Configurar o prompt do agente
            system_prompt = agent_config.get('system_prompt', "Você é um assistente prestativo.")
            
            # Criar e executar o agente
            agent_executor = BaseAgent(
                rag_system=rag_system,
                model_name=agent_config.get('model_name', 'gpt-3.5-turbo'),
                temperature=agent_config.get('temperature', 0.7),
                system_prompt=system_prompt,
                tools=['rag_query', 'search_documents'],
                memory=agent_config.get('memory', True)
            )
            
            response = agent_executor.run(question)
            
            return {'success': True, 'response': response}
            
        except Exception as e:
            logger.error(f"Erro ao consultar agente: {e}")
            return {'success': False, 'error': str(e)}

# Instância do gerenciador
agent_manager = AgentManager()


# --- Rotas da Interface Web ---

@app.route('/')
def index():
    """Página principal que exibe o dashboard com a lista de agentes"""
    agents = agent_manager.get_all_agents()
    return render_template('index.html', agents=agents)

@app.route('/agents')
def agents_page():
    """Página que exibe todos os agentes"""
    agents = agent_manager.get_all_agents()
    return render_template('agents.html', agents=agents)

@app.route('/agent/<agent_id>')
def agent_detail(agent_id):
    """Página de detalhes de um agente (chat, upload, etc)"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        return "Agente não encontrado", 404
    return render_template('agent_detail.html', agent=agent)


# --- Rotas da API ---

@app.route('/api/agents', methods=['GET'])
def api_get_agents():
    """Retorna lista de todos os agentes"""
    agents = agent_manager.get_all_agents()
    return jsonify(agents)

@app.route('/api/agents/<agent_id>', methods=['GET'])
def api_get_agent(agent_id):
    """Retorna dados de um agente específico"""
    agent = agent_manager.get_agent(agent_id)
    if agent:
        return jsonify(agent)
    return jsonify({'error': 'Agente não encontrado'}), 404

@app.route('/api/agents', methods=['POST'])
def api_create_agent():
    """API: Criar um novo agente"""
    try:
        data = request.json
        if not data or 'name' not in data or 'description' not in data:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        agent_id = agent_manager.create_agent(data)
        return jsonify({'success': True, 'agent_id': agent_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<agent_id>', methods=['PUT'])
def api_update_agent(agent_id):
    """API: Atualizar um agente"""
    try:
        data = request.json
        if not agent_manager.update_agent(agent_id, data):
            return jsonify({'error': 'Agente não encontrado'}), 404
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def api_delete_agent(agent_id):
    """API: Deletar um agente"""
    if not agent_manager.delete_agent(agent_id):
        return jsonify({'error': 'Agente não encontrado'}), 404
    return jsonify({'success': True})

@app.route('/api/agents/<agent_id>/upload', methods=['POST'])
def api_upload_files(agent_id):
    """API: Upload de arquivos para um agente"""
    if 'files' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    files = request.files.getlist('files')
    result = agent_manager.upload_files_to_agent(agent_id, files)
    
    return jsonify(result)

@app.route('/api/agents/<agent_id>/files', methods=['GET'])
def api_get_agent_files(agent_id):
    """API: Listar arquivos de um agente"""
    files = agent_manager.get_agent_files(agent_id)
    return jsonify(files)

@app.route('/api/agents/<agent_id>/files/<filename>', methods=['DELETE'])
def api_delete_agent_file(agent_id, filename):
    """API: Deletar um arquivo de um agente"""
    success = agent_manager.delete_agent_file(agent_id, filename)
    return jsonify({'success': success})

@app.route('/api/agents/<string:agent_id>/query', methods=['POST'])
def query_agent(agent_id):
    """Consulta um agente específico"""
    try:
        data = request.json
        user_input = data.get('input')
        
        agent_data = agent_manager.get_agent(agent_id)
        if not agent_data:
            return jsonify({"error": "Agente não encontrado"}), 404

        # Caminho para o diretório de upload e vector_db específico do agente
        agent_upload_dir = agent_data['folder_path']
        agent_vector_db_path = agent_data['vector_db_path']

        # Inicializar o RAGSystem para o agente
        rag_system = RAGSystem(
            upload_dir=agent_upload_dir,
            vector_db_path=agent_vector_db_path,
            collection_name=f"agent_{agent_id}"
        )

        system_prompt = agent_data.get('system_prompt') or "Você é um assistente de IA. Responda às perguntas com base nos documentos fornecidos."

        # Criar a configuração do agente
        config = AgentConfig(
            model_name=agent_data.get('model_name', 'gpt-4o-mini'),
            temperature=float(agent_data.get('temperature', 0.7)),
            system_prompt=system_prompt,
            tools=agent_data.get('tools', ['rag_query', 'search_documents']),
            memory=agent_data.get('memory', True),
            max_iterations=int(agent_data.get('max_iterations', 5))
        )

        # Criar e executar o agente
        agent_executor = BaseAgent(
            config=config,
            rag_system=rag_system
        )
        
        response = agent_executor.run(user_input)
        
        return jsonify({"response": response})

    except Exception as e:
        logging.error(f"Erro ao consultar agente: {e}")
        # Use str(e) para garantir que a exceção seja serializável para JSON
        return jsonify({"response": f"Ocorreu um erro: {str(e)}"})

@app.route('/download/<agent_id>')
def download_agent_files(agent_id):
    """Rota para baixar todos os arquivos de um agente como ZIP"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        return "Agente não encontrado", 404

    agent_folder = Path(agent['folder_path'])
    if not any(agent_folder.iterdir()):
        flash("Este agente não possui arquivos para download.")
        return redirect(url_for('agent_detail', agent_id=agent_id))

    zip_path = Path(f"temp/{agent_id}.zip")
    zip_path.parent.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in agent_folder.rglob('*'):
            zipf.write(file, file.relative_to(agent_folder))

    return send_file(zip_path, as_attachment=True, download_name=f"{agent['name']}_documentos.zip")

if __name__ == '__main__':
    # Limpar pasta temp ao iniciar
    if os.path.exists('temp'):
        shutil.rmtree('temp')
    os.makedirs('temp')
    
    app.run(debug=True, host='0.0.0.0', port=5000) 