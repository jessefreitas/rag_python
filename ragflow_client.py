"""
Cliente Python para integração com RAGFlow
Permite usar o RAGFlow como backend através de API REST
"""

import requests
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGFlowClient:
    """Cliente para integração com RAGFlow via API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Inicializa o cliente RAGFlow
        
        Args:
            base_url: URL base da API do RAGFlow
            api_key: Chave da API (se necessário)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
    
    def health_check(self) -> bool:
        """Verifica se a API do RAGFlow está funcionando"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro no health check: {e}")
            return False
    
    def upload_document(self, file_path: str, collection_name: str = "default") -> Dict[str, Any]:
        """
        Faz upload de um documento para o RAGFlow
        
        Args:
            file_path: Caminho para o arquivo
            collection_name: Nome da coleção
            
        Returns:
            Resposta da API com status do upload
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                data = {'collection_name': collection_name}
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/documents/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    logger.info(f"Documento {file_path.name} enviado com sucesso")
                    return response.json()
                else:
                    logger.error(f"Erro no upload: {response.status_code} - {response.text}")
                    return {'error': response.text}
                    
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {e}")
            return {'error': str(e)}
    
    def upload_documents_batch(self, file_paths: List[str], collection_name: str = "default") -> List[Dict[str, Any]]:
        """
        Faz upload de múltiplos documentos
        
        Args:
            file_paths: Lista de caminhos de arquivos
            collection_name: Nome da coleção
            
        Returns:
            Lista de resultados do upload
        """
        results = []
        for file_path in file_paths:
            result = self.upload_document(file_path, collection_name)
            results.append(result)
        return results
    
    def ask_question(self, question: str, collection_name: str = "default", 
                    include_sources: bool = True) -> Dict[str, Any]:
        """
        Faz uma pergunta ao RAGFlow
        
        Args:
            question: Pergunta a ser respondida
            collection_name: Nome da coleção
            include_sources: Se deve incluir fontes na resposta
            
        Returns:
            Resposta da API com a resposta e fontes
        """
        try:
            payload = {
                'question': question,
                'collection_name': collection_name,
                'include_sources': include_sources
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Pergunta respondida: '{question}'")
                return result
            else:
                logger.error(f"Erro na pergunta: {response.status_code} - {response.text}")
                return {'error': response.text}
                
        except Exception as e:
            logger.error(f"Erro ao fazer pergunta: {e}")
            return {'error': str(e)}
    
    def search_documents(self, query: str, collection_name: str = "default", 
                        limit: int = 5) -> Dict[str, Any]:
        """
        Busca documentos similares
        
        Args:
            query: Consulta de busca
            collection_name: Nome da coleção
            limit: Número máximo de resultados
            
        Returns:
            Documentos similares encontrados
        """
        try:
            payload = {
                'query': query,
                'collection_name': collection_name,
                'limit': limit
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/documents/search",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Busca realizada: '{query}' - {len(result.get('documents', []))} resultados")
                return result
            else:
                logger.error(f"Erro na busca: {response.status_code} - {response.text}")
                return {'error': response.text}
                
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return {'error': str(e)}
    
    def list_collections(self) -> Dict[str, Any]:
        """Lista todas as coleções disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/collections")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao listar coleções: {response.status_code} - {response.text}")
                return {'error': response.text}
                
        except Exception as e:
            logger.error(f"Erro ao listar coleções: {e}")
            return {'error': str(e)}
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Deleta uma coleção"""
        try:
            response = self.session.delete(f"{self.base_url}/api/v1/collections/{collection_name}")
            
            if response.status_code == 200:
                logger.info(f"Coleção {collection_name} deletada")
                return {'success': True}
            else:
                logger.error(f"Erro ao deletar coleção: {response.status_code} - {response.text}")
                return {'error': response.text}
                
        except Exception as e:
            logger.error(f"Erro ao deletar coleção: {e}")
            return {'error': str(e)}
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Obtém informações de uma coleção específica"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/collections/{collection_name}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter info da coleção: {response.status_code} - {response.text}")
                return {'error': response.text}
                
        except Exception as e:
            logger.error(f"Erro ao obter info da coleção: {e}")
            return {'error': str(e)}

# Cliente integrado com o sistema RAG Python
class RAGFlowRAGSystem:
    """Sistema RAG que usa RAGFlow como backend"""
    
    def __init__(self, ragflow_url: str = "http://localhost:8000", 
                 collection_name: str = "rag_python_docs"):
        """
        Inicializa o sistema integrado
        
        Args:
            ragflow_url: URL do RAGFlow
            collection_name: Nome da coleção no RAGFlow
        """
        self.client = RAGFlowClient(ragflow_url)
        self.collection_name = collection_name
        
        # Verificar conexão
        if not self.client.health_check():
            logger.warning("RAGFlow não está acessível. Verifique se está rodando.")
    
    def load_documents(self, file_paths: List[str]) -> bool:
        """
        Carrega documentos no RAGFlow
        
        Args:
            file_paths: Lista de caminhos de arquivos
            
        Returns:
            True se carregado com sucesso
        """
        try:
            results = self.client.upload_documents_batch(file_paths, self.collection_name)
            
            # Verificar se todos os uploads foram bem-sucedidos
            success_count = sum(1 for r in results if 'error' not in r)
            
            if success_count == len(file_paths):
                logger.info(f"Todos os {len(file_paths)} documentos carregados com sucesso")
                return True
            else:
                logger.warning(f"Apenas {success_count}/{len(file_paths)} documentos carregados")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao carregar documentos: {e}")
            return False
    
    def query(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """
        Faz uma pergunta usando o RAGFlow
        
        Args:
            question: Pergunta a ser respondida
            include_sources: Se deve incluir fontes
            
        Returns:
            Resposta formatada
        """
        try:
            result = self.client.ask_question(question, self.collection_name, include_sources)
            
            if 'error' in result:
                return {
                    'answer': f"Erro: {result['error']}",
                    'sources': [],
                    'success': False
                }
            
            # Adaptar resposta do RAGFlow para o formato do RAG Python
            response = {
                'answer': result.get('answer', ''),
                'sources': result.get('sources', []),
                'success': True
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao fazer pergunta: {e}")
            return {
                'answer': f"Erro ao processar pergunta: {str(e)}",
                'sources': [],
                'success': False
            }
    
    def search_similar_documents(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Busca documentos similares
        
        Args:
            query: Consulta de busca
            k: Número de resultados
            
        Returns:
            Lista de documentos similares
        """
        try:
            result = self.client.search_documents(query, self.collection_name, k)
            
            if 'error' in result:
                logger.error(f"Erro na busca: {result['error']}")
                return []
            
            documents = result.get('documents', [])
            
            # Adaptar formato para compatibilidade
            formatted_docs = []
            for doc in documents:
                formatted_docs.append({
                    'content': doc.get('content', ''),
                    'metadata': doc.get('metadata', {})
                })
            
            return formatted_docs
            
        except Exception as e:
            logger.error(f"Erro na busca de documentos: {e}")
            return []
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema"""
        try:
            collection_info = self.client.get_collection_info(self.collection_name)
            
            if 'error' in collection_info:
                return {
                    'ragflow_status': 'error',
                    'collection_name': self.collection_name,
                    'error': collection_info['error']
                }
            
            return {
                'ragflow_status': 'connected',
                'collection_name': self.collection_name,
                'document_count': collection_info.get('document_count', 0),
                'ragflow_url': self.client.base_url
            }
            
        except Exception as e:
            return {
                'ragflow_status': 'error',
                'collection_name': self.collection_name,
                'error': str(e)
            } 