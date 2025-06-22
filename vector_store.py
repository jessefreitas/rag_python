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
import psycopg2
from langchain.schema import Document
from pgvector.psycopg2 import register_vector
from llm_providers import llm_manager
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# O modelo de embedding a ser usado. Certifique-se que o provider está configurado.
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536  # Dimensões para text-embedding-3-small

class SecurityError(Exception):
    """Erro de segurança para violações de isolamento de agente"""
    pass

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

class PGVectorStore:
    """
    Gerencia o armazenamento e a busca de vetores no PostgreSQL/Supabase
    usando a extensão pgvector, de forma específica para cada agente.
    """
    def __init__(self, agent_id: str):
        if not agent_id:
            raise ValueError("PGVectorStore requer um agent_id.")
        self.agent_id = agent_id
        self.embedding_function = self._get_embedding_function()

    def _get_embedding_function(self):
        """Retorna a função de embedding usando OpenAI diretamente."""
        def embed_texts(texts: List[str]) -> List[List[float]]:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                embeddings = []
                for text in texts:
                    response = client.embeddings.create(
                        model=EMBEDDING_MODEL,
                        input=text
                    )
                    embeddings.append(response.data[0].embedding)
                
                return embeddings
            except Exception as e:
                logger.error(f"Erro ao gerar embeddings: {e}")
                raise

        return embed_texts

    def _execute_query(self, query: str, params: tuple = (), fetch: str = None):
        """Executa uma query no banco de dados."""
        conn = None
        try:
            conn = Database.get_connection()
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch == 'one':
                    return cur.fetchone()
                if fetch == 'all':
                    return cur.fetchall()
                conn.commit()
        except Exception as e:
            logger.error(f"Erro na query ao banco de dados: {e}", exc_info=True)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                Database.release_connection(conn)

    def add_documents(self, documents: List[Document]):
        """Gera embeddings para os documentos e os salva no banco de dados."""
        logger.info(f"🔗 PGVectorStore: Iniciando adição de {len(documents)} documentos para agente {self.agent_id}")
        
        # Verificar se há documentos para processar
        if not documents:
            logger.warning(f"⚠️ PGVectorStore: Nenhum documento fornecido para o agente {self.agent_id}")
            return
        
        texts = [doc.page_content for doc in documents]
        logger.info(f"📝 PGVectorStore: Extraídos {len(texts)} textos dos documentos")
        
        # Verificar se há textos válidos
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            logger.warning(f"⚠️ PGVectorStore: Nenhum texto válido encontrado para o agente {self.agent_id}")
            return
        
        logger.info(f"🧠 PGVectorStore: Gerando embeddings para {len(valid_texts)} textos...")
        embeddings = self.embedding_function(valid_texts)
        logger.info(f"✅ PGVectorStore: Embeddings gerados com sucesso ({len(embeddings)} embeddings)")

        # Usando a nova estrutura de tabelas
        # Primeiro, precisamos criar um 'document' mestre para estes chunks
        source = documents[0].metadata.get('source', 'desconhecido') if documents else 'desconhecido'
        logger.info(f"📂 PGVectorStore: Fonte do documento: {source}")
        
        # Usar uma única transação para garantir consistência
        conn = None
        try:
            conn = Database.get_connection()
            register_vector(conn)
            
            with conn.cursor() as cur:
                # Insere um novo documento na tabela 'documents' para obter um ID
                logger.info(f"💾 PGVectorStore: Inserindo documento mestre na tabela 'documents'...")
                doc_query = "INSERT INTO documents (agent_id, file_name, source_type) VALUES (%s, %s, %s) RETURNING id"
                cur.execute(doc_query, (self.agent_id, source, 'file'))
                document_id = cur.fetchone()[0]
                logger.info(f"✅ PGVectorStore: Documento mestre criado com ID: {document_id}")

                # Agora, insere cada chunk associado a esse novo document_id
                logger.info(f"📄 PGVectorStore: Inserindo {len(valid_texts)} chunks na tabela 'document_chunks'...")
                chunk_query = "INSERT INTO document_chunks (document_id, agent_id, chunk_text, embedding) VALUES (%s, %s, %s, %s)"
                for i, text_chunk in enumerate(valid_texts):
                    logger.info(f"  - Inserindo chunk {i+1}/{len(valid_texts)} (tamanho: {len(text_chunk)} chars)")
                    cur.execute(chunk_query, (document_id, self.agent_id, text_chunk, embeddings[i]))
                
                # Commit da transação
                conn.commit()
                logger.info(f"🎉 PGVectorStore: {len(valid_texts)} chunks salvos no banco de dados para o agente {self.agent_id}")
                
        except Exception as e:
            logger.error(f"❌ PGVectorStore: Erro ao adicionar documentos: {e}", exc_info=True)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                Database.release_connection(conn)

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Busca por documentos similares a uma query APENAS do agente atual."""
        # Validação de segurança: garantir que agent_id não seja nulo/vazio
        if not self.agent_id or not isinstance(self.agent_id, str):
            raise ValueError(f"Agent ID inválido para busca: {self.agent_id}")
            
        logger.info(f"🔍 PGVectorStore: Iniciando busca por similaridade para agente {self.agent_id}")
        
        query_embedding = self.embedding_function([query])[0]
        logger.info(f"🧠 PGVectorStore: Embedding da query gerado ({len(query_embedding)} dimensões)")

        # Usar uma conexão dedicada para a busca
        conn = None
        try:
            conn = Database.get_connection()
            register_vector(conn)
            
            with conn.cursor() as cur:
                # ISOLAMENTO GARANTIDO: Busca APENAS chunks do agente específico
                # Usamos tanto WHERE agent_id = %s quanto validação dupla
                db_query = """
                    SELECT chunk_text, (embedding <=> %s::vector) AS distance, agent_id
                    FROM document_chunks
                    WHERE agent_id = %s
                    ORDER BY distance
                    LIMIT %s
                """
                
                logger.info(f"📊 PGVectorStore: Executando busca ISOLADA por {k} chunks do agente {self.agent_id}...")
                cur.execute(db_query, (query_embedding, self.agent_id, k))
                results = cur.fetchall()
                
                # Validação adicional de segurança: verificar se todos os resultados são do agente correto
                for row in results:
                    if row[2] != self.agent_id:  # row[2] é o agent_id retornado
                        logger.error(f"🚨 VIOLAÇÃO DE SEGURANÇA: Chunk de agente diferente detectado! Esperado: {self.agent_id}, Encontrado: {row[2]}")
                        raise SecurityError(f"Violação de isolamento de agente detectada")
                
                logger.info(f"✅ PGVectorStore: Encontrados {len(results)} chunks similares (APENAS do agente {self.agent_id})")
                
                return [Document(
                    page_content=row[0], 
                    metadata={
                        'distance': float(row[1]),
                        'agent_id': row[2],  # Para auditoria
                        'source_agent_verified': row[2] == self.agent_id
                    }
                ) for row in results]
                
        except Exception as e:
            logger.error(f"❌ PGVectorStore: Erro na busca por similaridade: {e}", exc_info=True)
            raise
        finally:
            if conn:
                Database.release_connection(conn) 