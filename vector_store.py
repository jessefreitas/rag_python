"""
Módulo para gerenciamento do banco de vetores usando ChromaDB
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Classe para gerenciar o banco de vetores usando ChromaDB"""
    
    def __init__(self, 
                 persist_directory: str = "./vector_db",
                 collection_name: str = "documents",
                 embedding_model: str = "text-embedding-ada-002"):
        """
        Inicializa o banco de vetores
        
        Args:
            persist_directory: Diretório para persistir os dados
            collection_name: Nome da coleção
            embedding_model: Modelo de embedding a ser usado
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Criar diretório se não existir
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Inicializar embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Inicializar vector store
        self.vector_store = None
        self._initialize_vector_store()
        
        logger.info(f"Vector store inicializado em: {self.persist_directory}")
    
    def _initialize_vector_store(self):
        """Inicializa o vector store"""
        try:
            # Verificar se já existe uma coleção
            collections = self.client.list_collections()
            collection_exists = any(col.name == self.collection_name for col in collections)
            
            if collection_exists:
                # Carregar coleção existente
                self.vector_store = Chroma(
                    client=self.client,
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(self.persist_directory)
                )
                logger.info(f"Coleção existente carregada: {self.collection_name}")
            else:
                # Criar nova coleção
                self.vector_store = Chroma(
                    client=self.client,
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(self.persist_directory)
                )
                logger.info(f"Nova coleção criada: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar vector store: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Any]) -> None:
        """
        Adiciona documentos ao banco de vetores
        
        Args:
            documents: Lista de documentos LangChain
        """
        try:
            if not documents:
                logger.warning("Nenhum documento fornecido para adicionar")
                return
            
            # Adicionar documentos ao vector store
            self.vector_store.add_documents(documents)
            
            # Persistir mudanças
            self.vector_store.persist()
            
            logger.info(f"Adicionados {len(documents)} documentos ao vector store")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {str(e)}")
            raise
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 4,
                         filter_dict: Optional[Dict] = None) -> List[Any]:
        """
        Realiza busca por similaridade
        
        Args:
            query: Consulta de busca
            k: Número de resultados a retornar
            filter_dict: Filtros opcionais
            
        Returns:
            Lista de documentos similares
        """
        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter_dict
            )
            
            logger.info(f"Busca realizada para: '{query}' - {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {str(e)}")
            raise
    
    def similarity_search_with_score(self, 
                                   query: str, 
                                   k: int = 4,
                                   filter_dict: Optional[Dict] = None) -> List[tuple]:
        """
        Realiza busca por similaridade retornando scores
        
        Args:
            query: Consulta de busca
            k: Número de resultados a retornar
            filter_dict: Filtros opcionais
            
        Returns:
            Lista de tuplas (documento, score)
        """
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )
            
            logger.info(f"Busca com score realizada para: '{query}' - {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca com score: {str(e)}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre a coleção
        
        Returns:
            Dicionário com informações da coleção
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            info = {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": str(self.persist_directory),
                "embedding_model": self.embedding_model
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações da coleção: {str(e)}")
            return {}
    
    def delete_collection(self) -> bool:
        """
        Deleta a coleção atual
        
        Returns:
            True se deletado com sucesso
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Coleção deletada: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar coleção: {str(e)}")
            return False
    
    def reset_vector_store(self) -> bool:
        """
        Reseta completamente o vector store
        
        Returns:
            True se resetado com sucesso
        """
        try:
            # Deletar coleção
            self.delete_collection()
            
            # Reinicializar
            self._initialize_vector_store()
            
            logger.info("Vector store resetado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao resetar vector store: {str(e)}")
            return False
    
    def get_document_sources(self) -> List[str]:
        """
        Obtém lista de fontes de documentos únicas
        
        Returns:
            Lista de fontes únicas
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            results = collection.get()
            
            if 'metadatas' in results and results['metadatas']:
                sources = set()
                for metadata in results['metadatas']:
                    if metadata and 'source' in metadata:
                        sources.add(metadata['source'])
                return list(sources)
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao obter fontes de documentos: {str(e)}")
            return [] 