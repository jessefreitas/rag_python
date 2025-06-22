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

from agent_system import AgentConfig, BaseAgent, MultiAgentSystem, create_agent, MultiLLMAgent
from rag_system import RAGSystem
from vector_store import VectorStore
from document_loader import DocumentLoader
from database import Database  # Importar a nova classe de banco de dados
from llm_providers import llm_manager  # Importar o gerenciador de provedores

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
        """Obtém lista de todos os agentes do banco de dados, incluindo contagem de documentos."""
        query = """
            SELECT
                a.id_agente,
                a.nome_agente,
                a.descricao,
                a.system_prompt,
                a.modelo_base,
                a.temperatura,
                a.criado_em,
                COUNT(d.id_doc) AS document_count
            FROM
                agentes a
            LEFT JOIN
                documentos_mestre d ON a.id_agente = d.id_agente
            GROUP BY
                a.id_agente
            ORDER BY
                a.criado_em DESC;
        """
        agents = self._execute_query(query, fetch='all')
        
        # Formatar agentes para a UI
        formatted_agents = []
        for agent in agents:
            formatted_agent = {
                'id': agent['id_agente'],
                'name': agent['nome_agente'],
                'description': agent['descricao'],
                'system_prompt': agent['system_prompt'],
                'model_name': agent['modelo_base'],
                'temperature': float(agent['temperatura']),
                'created_at': agent['criado_em'].isoformat(),
                'document_count': agent['document_count'],
                'folder_path': str(Path(UPLOAD_FOLDER) / str(agent['id_agente'])),
                'vector_db_path': str(Path('agent_vector_dbs') / str(agent['id_agente']))
            }
            formatted_agents.append(formatted_agent)
        
        return formatted_agents

    def get_agent_documents(self, agent_id: str) -> List[Dict[str, Any]]:
        """Obtém documentos de um agente específico."""
        query = """
            SELECT id_doc, nome_arquivo, tipo_documento, tamanho_bytes, criado_em
            FROM documentos_mestre
            WHERE id_agente = %s
            ORDER BY criado_em DESC;
        """
        documents = self._execute_query(query, (agent_id,), fetch='all')
        
        formatted_docs = []
        for doc in documents:
            formatted_doc = {
                'id': doc['id_doc'],
                'filename': doc['nome_arquivo'],
                'type': doc['tipo_documento'],
                'size': doc['tamanho_bytes'],
                'created_at': doc['criado_em'].isoformat()
            }
            formatted_docs.append(formatted_doc)
        
        return formatted_docs

    def get_dashboard_stats(self) -> Dict[str, int]:
        """Calcula e retorna estatísticas para o dashboard principal."""
        stats = {
            'total_agents': 0,
            'total_documents': 0,
            'good_ratings': 0,
            'bad_ratings': 0
        }
        try:
            # Contar agentes
            agents_query = "SELECT COUNT(*) as count FROM agentes WHERE status = 'ativo';"
            agents_result = self._execute_query(agents_query, fetch='one')
            if agents_result:
                stats['total_agents'] = agents_result['count']

            # Contar documentos
            docs_query = "SELECT COUNT(*) as count FROM documentos_mestre;"
            docs_result = self._execute_query(docs_query, fetch='one')
            if docs_result:
                stats['total_documents'] = docs_result['count']

            # Contar avaliações
            ratings_query = "SELECT satisfacao, COUNT(*) as count FROM interacoes_usuarios GROUP BY satisfacao;"
            ratings_results = self._execute_query(ratings_query, fetch='all')
            
            if ratings_results:
                for row in ratings_results:
                    if row['satisfacao'] == 5:
                        stats['good_ratings'] = row['count']
                    elif row['satisfacao'] == 1:
                        stats['bad_ratings'] = row['count']
            return stats
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas do dashboard: {e}")
            return stats # Retorna stats zerados em caso de erro

    def get_agent_stats(self, agent_id: str) -> Dict[str, int]:
        """Calcula e retorna estatísticas para um agente específico."""
        stats = {
            'total_documents': 0,
            'good_ratings': 0,
            'bad_ratings': 0
        }
        try:
            # Contar documentos do agente
            doc_query = "SELECT COUNT(*) as count FROM documentos_mestre WHERE id_agente = %s;"
            doc_result = self._execute_query(doc_query, (agent_id,), fetch='one')
            if doc_result:
                stats['total_documents'] = doc_result['count']

            # Contar avaliações do agente
            ratings_query = "SELECT satisfacao, COUNT(*) as count FROM interacoes_usuarios WHERE id_agente = %s GROUP BY satisfacao;"
            ratings_results = self._execute_query(ratings_query, (agent_id,), fetch='all')
            
            if ratings_results:
                for row in ratings_results:
                    if row['satisfacao'] == 5:
                        stats['good_ratings'] = row['count']
                    elif row['satisfacao'] == 1:
                        stats['bad_ratings'] = row['count']
            return stats
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas para o agente {agent_id}: {e}")
            return stats

    def upload_files_to_agent(self, agent_id: str, files: List) -> Dict[str, Any]:
        """Faz upload de arquivos para um agente específico"""
        try:
            agent_folder = Path(UPLOAD_FOLDER) / agent_id
            agent_folder.mkdir(parents=True, exist_ok=True)
            
            uploaded_files = []
            for file in files:
                if file and self.allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = agent_folder / filename
                    file.save(str(file_path))
                    
                    # Calcular hash do arquivo
                    file_hash = self._calculate_file_hash(file_path)
                    
                    # Salvar no banco de dados
                    doc_id = str(uuid.uuid4())
                    query = """
                        INSERT INTO documentos_mestre (id_doc, id_agente, nome_arquivo, tipo_documento, tamanho_bytes, hash_arquivo, caminho_arquivo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    params = (
                        doc_id,
                        agent_id,
                        filename,
                        Path(filename).suffix.lower(),
                        file_path.stat().st_size,
                        file_hash,
                        str(file_path)
                    )
                    self._execute_query(query, params)
                    
                    uploaded_files.append({
                        'filename': filename,
                        'size': file_path.stat().st_size,
                        'hash': file_hash
                    })
                    
                    logger.info(f"Arquivo {filename} carregado para agente {agent_id}")
            
            return {
                'success': True,
                'uploaded_files': uploaded_files,
                'message': f'{len(uploaded_files)} arquivo(s) carregado(s) com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro no upload de arquivos: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_agent_files(self, agent_id: str) -> List[Dict[str, Any]]:
        """Obtém lista de arquivos de um agente"""
        try:
            query = """
                SELECT nome_arquivo, tipo_documento, tamanho_bytes, criado_em
                FROM documentos_mestre
                WHERE id_agente = %s
                ORDER BY criado_em DESC;
            """
            files = self._execute_query(query, (agent_id,), fetch='all')
            
            formatted_files = []
            for file in files:
                formatted_files.append({
                    'filename': file['nome_arquivo'],
                    'type': file['tipo_documento'],
                    'size': file['tamanho_bytes'],
                    'created_at': file['criado_em'].isoformat()
                })
            
            return formatted_files
            
        except Exception as e:
            logger.error(f"Erro ao obter arquivos do agente: {e}")
            return []

    def delete_agent_file(self, agent_id: str, filename: str) -> bool:
        """Deleta um arquivo específico de um agente"""
        try:
            # Buscar informações do arquivo no banco
            query = "SELECT caminho_arquivo FROM documentos_mestre WHERE id_agente = %s AND nome_arquivo = %s;"
            result = self._execute_query(query, (agent_id, filename), fetch='one')
            
            if result:
                file_path = Path(result['caminho_arquivo'])
                if file_path.exists():
                    file_path.unlink()  # Deletar arquivo físico
                
                # Deletar registro do banco
                delete_query = "DELETE FROM documentos_mestre WHERE id_agente = %s AND nome_arquivo = %s;"
                self._execute_query(delete_query, (agent_id, filename))
                
                logger.info(f"Arquivo {filename} deletado do agente {agent_id}")
                return True
            else:
                logger.warning(f"Arquivo {filename} não encontrado para o agente {agent_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            return False

    def save_interaction(self, agent_id: str, user_input: str, agent_response: str, rating: str) -> bool:
        """Salva uma interação do usuário com o agente"""
        try:
            # Converter rating para número
            rating_value = 5 if rating == "good" else 1
            
            query = """
                INSERT INTO interacoes_usuarios (id_agente, entrada_usuario, resposta_agente, satisfacao)
                VALUES (%s, %s, %s, %s);
            """
            self._execute_query(query, (agent_id, user_input, agent_response, rating_value))
            
            logger.info(f"Interação salva para agente {agent_id} com rating {rating}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar interação: {e}")
            return False

    def allowed_file(self, filename: str) -> bool:
        """Verifica se o arquivo tem extensão permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula o hash SHA-256 de um arquivo"""
        import hashlib
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def query_agent(self, agent_id: str, question: str, use_multi_llm: bool = False, providers: List[str] = None) -> Dict[str, Any]:
        """Executa uma consulta usando um agente específico"""
        try:
            # Obter informações do agente
            agent_info = self.get_agent(agent_id)
            if not agent_info:
                return {"error": "Agente não encontrado"}
            
            # Criar sistema RAG para o agente
            vector_db_path = agent_info['vector_db_path']
            rag_system = RAGSystem(
                vector_db_path=vector_db_path,
                model_name=agent_info['model_name'],
                temperature=agent_info['temperature'],
                provider="openai"
            )
            
            if use_multi_llm:
                # Usar agente multi-LLM
                providers = providers or ['openai', 'openrouter']
                config = AgentConfig(
                    agent_id=agent_id,
                    agent_name=agent_info['name'],
                    model_name=agent_info['model_name'],
                    temperature=agent_info['temperature'],
                    system_prompt=agent_info['system_prompt'],
                    provider="multi"
                )
                
                multi_agent = MultiLLMAgent(config, rag_system, providers)
                result = multi_agent.process_message_multi_llm(question)
                
                return {
                    "multi_llm": True,
                    "responses": result['responses'],
                    "errors": result['errors'],
                    "comparison": result['comparison'],
                    "agent_name": agent_info['name'],
                    "providers_used": list(result['responses'].keys())
                }
            else:
                # Usar agente normal
                config = AgentConfig(
                    agent_id=agent_id,
                    agent_name=agent_info['name'],
                    model_name=agent_info['model_name'],
                    temperature=agent_info['temperature'],
                    system_prompt=agent_info['system_prompt'],
                    provider="openai"
                )
                
                agent = BaseAgent(config, rag_system)
                response = agent.process_message(question)
                
                return {
                    "multi_llm": False,
                    "response": response,
                    "agent_name": agent_info['name'],
                    "model_name": agent_info['model_name']
                }
            
        except Exception as e:
            logger.error(f"Erro ao consultar agente: {e}")
            return {"error": f"Erro ao processar pergunta: {str(e)}"}

# Inicializar o gerenciador de agentes
agent_manager = AgentManager()

# Rotas da aplicação
@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/agents')
def agents_page():
    """Página de listagem de agentes"""
    return render_template('agents.html')

@app.route('/agent/<agent_id>')
def agent_detail(agent_id):
    """Página de detalhes de um agente específico"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        return "Agente não encontrado", 404
    return render_template('agent_detail.html', agent=agent)

# Rotas da API
@app.route('/api/v1/dashboard/stats', methods=['GET'])
def api_v1_get_dashboard_stats():
    """Retorna as estatísticas para o dashboard principal."""
    stats = agent_manager.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/v1/providers', methods=['GET'])
def api_v1_get_providers():
    """Retorna informações sobre os provedores de IA disponíveis."""
    try:
        provider_info = llm_manager.get_provider_info()
        return jsonify(provider_info)
    except Exception as e:
        logger.error(f"Erro ao obter informações dos provedores: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/providers/<provider_name>/models', methods=['GET'])
def api_v1_get_provider_models(provider_name):
    """Retorna os modelos disponíveis para um provedor específico."""
    try:
        models = llm_manager.get_provider_models(provider_name)
        return jsonify({"provider": provider_name, "models": models})
    except Exception as e:
        logger.error(f"Erro ao obter modelos do provedor {provider_name}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/agents', methods=['GET', 'POST'])
def api_v1_handle_agents():
    """Lida com a criação (POST) e listagem (GET) de agentes."""
    if request.method == 'POST':
        try:
            agent_data = request.json
            agent_id = agent_manager.create_agent(agent_data)
            return jsonify({"success": True, "agent_id": agent_id}), 201
        except Exception as e:
            logger.error(f"Erro ao criar agente: {e}")
            return jsonify({"error": str(e)}), 500
    else:  # GET
        try:
            agents = agent_manager.get_all_agents()
            return jsonify(agents)
        except Exception as e:
            logger.error(f"Erro ao listar agentes: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/v1/agents/<agent_id>', methods=['GET', 'PUT', 'DELETE'])
def api_v1_agent_detail(agent_id):
    """Lida com operações específicas de um agente."""
    if request.method == 'GET':
        agent = agent_manager.get_agent(agent_id)
        if not agent:
            return jsonify({"error": "Agente não encontrado"}), 404
        return jsonify(agent)
    elif request.method == 'PUT':
        try:
            agent_data = request.json
            success = agent_manager.update_agent(agent_id, agent_data)
            return jsonify({"success": success})
        except Exception as e:
            logger.error(f"Erro ao atualizar agente: {e}")
            return jsonify({"error": str(e)}), 500
    elif request.method == 'DELETE':
        try:
            success = agent_manager.delete_agent(agent_id)
            return jsonify({"success": success})
        except Exception as e:
            logger.error(f"Erro ao deletar agente: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/v1/agents/<agent_id>/upload', methods=['POST'])
def api_v1_upload_files(agent_id):
    """Faz upload de arquivos para um agente específico."""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        files = request.files.getlist('files')
        result = agent_manager.upload_files_to_agent(agent_id, files)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/agents/<agent_id>/files', methods=['GET'])
def api_v1_get_agent_files(agent_id):
    """Obtém lista de arquivos de um agente."""
    files = agent_manager.get_agent_files(agent_id)
    return jsonify(files)

@app.route('/api/v1/agents/<agent_id>/files/<filename>', methods=['DELETE'])
def api_v1_delete_agent_file(agent_id, filename):
    """Deleta um arquivo específico de um agente."""
    success = agent_manager.delete_agent_file(agent_id, filename)
    return jsonify({"success": success})

@app.route('/api/v1/agents/<string:agent_id>/feedback', methods=['POST'])
def api_v1_handle_feedback(agent_id):
    """Processa feedback do usuário sobre uma resposta do agente."""
    try:
        data = request.json
        user_input = data.get('user_input', '')
        agent_response = data.get('agent_response', '')
        rating = data.get('rating', 'neutral')  # 'good', 'bad', 'neutral'
        
        if rating in ['good', 'bad']:
            success = agent_manager.save_interaction(agent_id, user_input, agent_response, rating)
            return jsonify({"success": success})
        else:
            return jsonify({"success": True, "message": "Feedback neutro ignorado"})
            
    except Exception as e:
        logger.error(f"Erro ao processar feedback: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/agents/<string:agent_id>/query', methods=['POST'])
def api_v1_query_agent_route(agent_id):
    """Executa uma consulta usando um agente específico."""
    try:
        data = request.json
        question = data.get('question', '')
        use_multi_llm = data.get('use_multi_llm', False)
        providers = data.get('providers', ['openai', 'openrouter'])
        
        if not question:
            return jsonify({"error": "Pergunta não fornecida"}), 400
        
        result = agent_manager.query_agent(agent_id, question, use_multi_llm, providers)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao consultar agente: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download/<agent_id>')
def download_agent_files(agent_id):
    # Lógica de download (pode precisar ser implementada)
    return "Funcionalidade de download ainda não implementada.", 501

@app.route('/api/v1/agents/<agent_id>/stats', methods=['GET'])
def api_v1_get_agent_stats(agent_id):
    """Retorna as estatísticas para um agente específico."""
    stats = agent_manager.get_agent_stats(agent_id)
    return jsonify(stats)

if __name__ == '__main__':
    # Executa a aplicação Flask, tornando-acessível na rede local
    app.run(host='0.0.0.0', port=5000, debug=True) 