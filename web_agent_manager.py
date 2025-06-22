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
import hashlib

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import zipfile

from agent_system import AgentConfig, BaseAgent, MultiAgentSystem
from rag_system import RAGSystem
from vector_store import VectorStore
from document_loader import DocumentLoader
from database import Database  # Importar a nova classe de banco de dados

# Configuração de logging (MOVIDO PARA CIMA)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Inicializar o pool de conexões com o banco de dados
try:
    Database.initialize_pool()
except Exception as e:
    logger.error(f"FALHA AO INICIALIZAR O BANCO DE DADOS: {e}")
    # A aplicação pode continuar, mas as operações de banco de dados falharão.
    # Em um ambiente de produção, você pode querer sair aqui.

class AgentManager:
    """Gerenciador de agentes e seus documentos usando PostgreSQL"""
    
    def __init__(self):
        # O construtor agora está mais simples, sem carregar arquivos.
        pass

    def _execute_query(self, query, params=None, fetch=None):
        """Função auxiliar para executar consultas no banco de dados."""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
                result = None
                if fetch == 'one':
                    record = cursor.fetchone()
                    if record:
                        columns = [desc[0] for desc in cursor.description]
                        result = dict(zip(columns, record))
                elif fetch == 'all':
                    records = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    result = [dict(zip(columns, row)) for row in records]
                
                # Commit a transação para salvar as alterações
                conn.commit()
                
                if fetch:
                    return result
                return cursor
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                Database.release_connection(conn)

    def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """Cria um novo agente no banco de dados."""
        agent_id = str(uuid.uuid4())
        agent_folder = Path(UPLOAD_FOLDER) / agent_id
        agent_folder.mkdir(parents=True, exist_ok=True)
        vector_db_folder = Path('agent_vector_dbs') / agent_id
        vector_db_folder.mkdir(parents=True, exist_ok=True)

        query = """
            INSERT INTO agentes (id_agente, nome_agente, descricao, system_prompt, modelo_base, temperatura, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_agente;
        """
        params = (
            agent_id,
            agent_data['name'],
            agent_data['description'],
            agent_data.get('system_prompt', 'Você é um assistente prestativo.'),
            agent_data.get('model_name', 'gpt-3.5-turbo'),
            float(agent_data.get('temperature', 0.7)),
            'ativo'
        )
        new_agent_id = self._execute_query(query, params, fetch='one')['id_agente']
        logger.info(f"Agente criado no DB: {agent_data['name']} (ID: {new_agent_id})")
        return new_agent_id

    def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """Atualiza um agente existente no banco de dados."""
        query = """
            UPDATE agentes
            SET nome_agente = %s, descricao = %s, system_prompt = %s, modelo_base = %s, temperatura = %s
            WHERE id_agente = %s;
        """
        params = (
            agent_data.get('name'),
            agent_data.get('description'),
            agent_data.get('system_prompt'),
            agent_data.get('model_name'),
            float(agent_data.get('temperature')),
            agent_id
        )
        self._execute_query(query, params)
        logger.info(f"Agente atualizado no DB: {agent_id}")
        return True

    def delete_agent(self, agent_id: str) -> bool:
        """Deleta um agente do banco de dados e remove seus arquivos."""
        # Primeiro, remover pastas para evitar arquivos órfãos se o delete no DB falhar
        agent_info = self.get_agent(agent_id)
        if agent_info:
             # O caminho das pastas será reconstruído com base no ID
            agent_folder = Path(UPLOAD_FOLDER) / agent_id
            vector_db_folder = Path('agent_vector_dbs') / agent_id
            if agent_folder.exists():
                shutil.rmtree(agent_folder)
            if vector_db_folder.exists():
                shutil.rmtree(vector_db_folder)
        
        query = "DELETE FROM agentes WHERE id_agente = %s;"
        self._execute_query(query, (agent_id,))
        logger.info(f"Agente deletado do DB: {agent_id}")
        return True

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um agente do banco de dados de forma padronizada."""
        query = "SELECT * FROM agentes WHERE id_agente = %s;"
        agent = self._execute_query(query, (agent_id,), fetch='one')
        if agent:
            # Padroniza as chaves do dicionário para serem consistentes com a UI
            formatted_agent = {
                'id': agent['id_agente'],
                'name': agent['nome_agente'],
                'description': agent['descricao'],
                'system_prompt': agent['system_prompt'],
                'model_name': agent['modelo_base'],
                'temperature': float(agent['temperatura']),
                'created_at': agent['criado_em'].isoformat(),
                # Adiciona caminhos de pasta dinamicamente
                'folder_path': str(Path(UPLOAD_FOLDER) / str(agent['id_agente'])),
                'vector_db_path': str(Path('agent_vector_dbs') / str(agent['id_agente']))
            }
            return formatted_agent
        return None

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Obtém lista de todos os agentes do banco de dados."""
        query = "SELECT * FROM agentes ORDER BY criado_em DESC;"
        agents = self._execute_query(query, fetch='all')
        # Renomeia as colunas para corresponder ao que a interface espera
        formatted_agents = []
        for agent in agents:
            formatted_agents.append({
                'id': agent['id_agente'],
                'name': agent['nome_agente'],
                'description': agent['descricao'],
                'system_prompt': agent['system_prompt'],
                'model_name': agent['modelo_base'],
                'temperature': float(agent['temperatura']),
                'created_at': agent['criado_em'].isoformat()
                # Adicionar outros campos se necessário pela interface
            })
        return formatted_agents
    
    # Os métodos de manipulação de arquivos (upload, get_files, delete_file)
    # permanecem em grande parte os mesmos, mas usarão get_agent para
    # obter o caminho da pasta do agente.

    def upload_files_to_agent(self, agent_id: str, files: List) -> Dict[str, Any]:
        """Faz upload de arquivos para um agente específico"""
        try:
            agent_info = self.get_agent(agent_id)
            if not agent_info:
                return {'success': False, 'error': 'Agente não encontrado'}

            agent_folder = Path(agent_info['folder_path'])
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
            
            return {
                'success': True,
                'uploaded_files': uploaded_files,
                'errors': errors,
                'total_files': len(uploaded_files)
            }
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_agent_files(self, agent_id: str) -> List[Dict[str, Any]]:
        """Obtém lista de arquivos de um agente"""
        try:
            agent_info = self.get_agent(agent_id)
            if not agent_info:
                return []

            agent_folder = Path(agent_info['folder_path'])
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
            agent_info = self.get_agent(agent_id)
            if not agent_info:
                return False

            agent_folder = Path(agent_info['folder_path'])
            file_path = agent_folder / filename
            
            if file_path.exists():
                file_path.unlink()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            return False

    def allowed_file(self, filename: str) -> bool:
        """Verifica se a extensão do arquivo é permitida."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def query_agent(self, agent_id: str, question: str) -> Dict[str, Any]:
        """Executa uma consulta em um agente específico."""
        try:
            # 1. Obter detalhes do agente do DB
            agent_details = self.get_agent(agent_id)
            if not agent_details:
                raise ValueError("Agente não encontrado")

            # 2. Configurar o sistema RAG para este agente
            agent_config = AgentConfig(
                agent_id=agent_details['id'],
                agent_name=agent_details['name'],
                system_prompt=agent_details['system_prompt'],
                model_name=agent_details['model_name'],
                temperature=float(agent_details['temperature'])
            )

            # Correção: Instanciar RAGSystem apenas com o caminho do DB de vetores
            rag_system = RAGSystem(vector_db_path=agent_details['vector_db_path'])

            # 3. Inicializar e executar o agente
            agent = BaseAgent(config=agent_config, rag_system=rag_system)
            
            # Usar o método .run() da nossa classe BaseAgent, que já lida com a lógica do invoke
            response = agent.run(question)
            
            return {"response": response}

        except Exception as e:
            logger.error(f"Erro ao consultar agente {agent_id}: {e}")
            # Re-lança a exceção para que a rota da API possa tratá-la
            raise

# Instância do gerenciador
agent_manager = AgentManager()


# --- Rotas da Aplicação Web (Páginas) ---

@app.route('/')
def index():
    """Página principal que redireciona para a listagem de agentes."""
    return redirect(url_for('agents_page'))

@app.route('/agents')
def agents_page():
    """Página principal que exibe e gerencia os agentes."""
    return render_template('agents.html')

@app.route('/agent/<agent_id>')
def agent_detail(agent_id):
    """Página de detalhes de um agente (chat, upload, etc)"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        return "Agente não encontrado", 404
    
    # Busca os arquivos do agente (a lógica pode ser movida para AgentManager)
    agent_folder = Path(UPLOAD_FOLDER) / agent_id
    files_list = []
    if agent_folder.exists():
        for file_path in agent_folder.iterdir():
            if file_path.is_file():
                files_list.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
    
    return render_template('agent_detail.html', agent=agent, files=files_list)


# --- Rotas da API (para interações via JavaScript) ---

@app.route('/api/agents', methods=['GET', 'POST'])
def handle_agents():
    """Lida com a criação e listagem de agentes."""
    if request.method == 'POST':
        # Lógica de criação (antiga api_create_agent)
        data = request.get_json()
        if not data or not data.get('name') or not data.get('description'):
            return jsonify({'error': 'Nome e descrição são obrigatórios'}), 400
        try:
            agent_id = agent_manager.create_agent(data)
            agent = agent_manager.get_agent(agent_id)
            return jsonify(agent), 201
        except Exception as e:
            logger.error(f"Erro ao criar agente: {e}")
            return jsonify({'error': f'Erro interno ao criar agente: {e}'}), 500
            
    elif request.method == 'GET':
        # Lógica de listagem (antiga api_get_agents)
        try:
            agents = agent_manager.get_all_agents()
            return jsonify(agents)
        except Exception as e:
            logger.error(f"Erro ao listar agentes: {e}")
            return jsonify({'error': f'Erro interno ao listar agentes: {e}'}), 500

@app.route('/api/agents/<agent_id>', methods=['GET'])
def api_get_agent(agent_id):
    """Obtém detalhes de um agente específico."""
    agent = agent_manager.get_agent(agent_id)
    if agent:
        return jsonify(agent)
    return jsonify({'error': 'Agente não encontrado'}), 404

@app.route('/api/agents/<agent_id>', methods=['PUT'])
def api_update_agent(agent_id):
    """Atualiza um agente existente."""
    data = request.get_json()
    if not agent_manager.update_agent(agent_id, data):
        return jsonify({'error': 'Agente não encontrado'}), 404
    return jsonify({'success': True})

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
    success = agent_manager.delete_agent_file(agent_id, filename)
    if success:
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Falha ao deletar o arquivo'}), 400

@app.route('/api/agents/<string:agent_id>/ingest_data', methods=['POST'])
def api_ingest_data(agent_id):
    """
    API: Recebe dados (ex: de uma extensão de navegador) e os ingere como um novo documento para um agente.
    """
    try:
        page_data = request.json
        if not page_data or 'content' not in page_data:
            return jsonify({'error': 'Dados inválidos. "content" é obrigatório.'}), 400

        agent = agent_manager.get_agent(agent_id)
        if not agent:
            return jsonify({'error': 'Agente não encontrado'}), 404

        # Aqui, futuramente, chamaremos um método mais robusto no AgentManager
        # para criar o documento, fazer o chunking e vetorizar.
        # Por enquanto, vamos simular a criação do documento.
        
        doc_text = page_data.get('content')
        doc_title = page_data.get('title', 'Sem Título')
        doc_url = page_data.get('url', '')

        # Lógica para salvar em 'documentos_mestre'
        # Esta lógica deve ser movida para o AgentManager em um próximo passo
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO documentos_mestre (id_agente, nome_arquivo, tipo_origem, texto_bruto, hash_md5)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_doc;
                """
                # Gera um hash simples para evitar duplicatas exatas
                hash_md5 = hashlib.md5(doc_text.encode()).hexdigest()
                
                params = (agent_id, doc_title, 'webapp_scrape', doc_text, hash_md5)
                
                cursor.execute(query, params)
                new_doc_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"Novo documento '{doc_title}' ingerido para o agente {agent_id} com ID: {new_doc_id}")
        finally:
            Database.release_connection(conn)

        # TODO: Chamar o processo de vetorização para este novo documento

        return jsonify({'success': True, 'message': f'Dados da página "{doc_title}" recebidos.', 'doc_id': new_doc_id}), 201

    except Exception as e:
        # Tratar erro de hash duplicado (violates unique constraint)
        if 'violates unique constraint' in str(e):
             return jsonify({'success': False, 'message': 'Este documento já existe na base de conhecimento.'}), 409
        
        logger.error(f"Erro ao ingerir dados: {e}")
        return jsonify({'error': f'Ocorreu um erro interno: {str(e)}'}), 500

@app.route('/api/agents/<agent_id>/process_files', methods=['POST'])
def api_process_agent_files(agent_id):
    """API: Processar (vetorizar) os arquivos de um agente"""
    try:
        agent = agent_manager.get_agent(agent_id)
        if not agent:
            return jsonify({'error': 'Agente não encontrado'}), 404
        
        # Inicializar RAGSystem para indexação
        rag_system = RAGSystem(
            upload_dir=agent['folder_path'],
            vector_db_path=agent['vector_db_path'],
            collection_name=f"agent_{agent_id}"
        )
        
        # Usar a classe DocumentLoader para carregar os arquivos
        doc_loader = DocumentLoader()
        documents = doc_loader.load_documents_from_directory(agent['folder_path'])
        
        # Indexar os documentos
        rag_system.add_documents(documents)
        
        logger.info(f"Arquivos do agente {agent_id} foram processados e vetorizados.")
        return jsonify({'success': True, 'message': f'{len(documents)} chunks de documentos foram processados.'})
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivos do agente {agent_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<string:agent_id>/query', methods=['POST'])
def query_agent_route(agent_id):
    """API: Envia uma pergunta para um agente e obtém uma resposta."""
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'A pergunta é obrigatória'}), 400

    try:
        result = agent_manager.query_agent(agent_id, question)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro na rota de query para o agente {agent_id}: {e}")
        return jsonify({'error': f'Ocorreu um erro interno: {e}'}), 500

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