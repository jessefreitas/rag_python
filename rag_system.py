"""
Sistema RAG (Retrieval-Augmented Generation) principal
Integra carregamento de documentos, banco de vetores e geração de respostas
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from document_loader import DocumentLoader
from vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    """Sistema RAG principal que integra todos os componentes"""
    
    def __init__(self, vector_db_path: str = "vector_db"):
        self.vector_db_path = vector_db_path
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore(
            collection_name=f"agent_{Path(vector_db_path).name}",
            persist_directory=self.vector_db_path
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        # Configurar API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY não configurada. Configure a variável de ambiente ou passe como parâmetro.")
        
        # Configurações
        self.model_name = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 1000
        
        # Inicializar modelo de linguagem
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Template de prompt personalizado
        self.prompt_template = PromptTemplate(
            template="""Você é um assistente útil que responde perguntas baseado no contexto fornecido.

Contexto:
{context}

Pergunta: {question}

Instruções:
1. Responda apenas com base no contexto fornecido
2. Se a informação não estiver no contexto, diga que não tem essa informação
3. Seja claro e conciso
4. Use linguagem natural e amigável
5. Cite as fontes quando relevante

Resposta:""",
            input_variables=["context", "question"]
        )
        
        # Inicializar chain de QA
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.vector_store.as_retriever(
                search_kwargs={"k": 4}
            ),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
        
        logger.info("Sistema RAG inicializado com sucesso")
    
    def load_documents(self, 
                      file_paths: Optional[List[str]] = None,
                      directory_path: Optional[str] = None,
                      urls: Optional[List[str]] = None) -> bool:
        """
        Carrega documentos para o sistema
        
        Args:
            file_paths: Lista de caminhos de arquivos
            directory_path: Caminho para diretório com documentos
            urls: Lista de URLs para carregar
            
        Returns:
            True se carregado com sucesso
        """
        try:
            all_documents = []
            
            # Carregar arquivos individuais
            if file_paths:
                for file_path in file_paths:
                    try:
                        documents = self.document_loader.load_document(file_path)
                        all_documents.extend(documents)
                        logger.info(f"Arquivo carregado: {file_path}")
                    except Exception as e:
                        logger.error(f"Erro ao carregar {file_path}: {str(e)}")
                        continue
            
            # Carregar diretório
            if directory_path:
                try:
                    documents = self.document_loader.load_documents_from_directory(directory_path)
                    all_documents.extend(documents)
                    logger.info(f"Diretório carregado: {directory_path}")
                except Exception as e:
                    logger.error(f"Erro ao carregar diretório {directory_path}: {str(e)}")
            
            # Carregar URLs
            if urls:
                for url in urls:
                    try:
                        if self.document_loader.validate_url(url):
                            documents = self.document_loader.load_web_page(url)
                            all_documents.extend(documents)
                            logger.info(f"URL carregada: {url}")
                        else:
                            logger.warning(f"URL inválida ou inacessível: {url}")
                    except Exception as e:
                        logger.error(f"Erro ao carregar URL {url}: {str(e)}")
                        continue
            
            # Adicionar ao banco de vetores
            if all_documents:
                self.vector_store.add_documents(all_documents)
                logger.info(f"Total de {len(all_documents)} documentos carregados no sistema")
                return True
            else:
                logger.warning("Nenhum documento foi carregado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao carregar documentos: {str(e)}")
            return False
    
    def query(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """
        Faz uma pergunta ao sistema RAG
        
        Args:
            question: Pergunta a ser respondida
            include_sources: Se deve incluir fontes na resposta
            
        Returns:
            Dicionário com resposta e fontes
        """
        try:
            if not question.strip():
                return {
                    "answer": "Por favor, forneça uma pergunta válida.",
                    "sources": [],
                    "success": False
                }
            
            # Fazer a consulta
            result = self.qa_chain({"query": question})
            
            response = {
                "answer": result["result"],
                "sources": [],
                "success": True
            }
            
            # Incluir fontes se solicitado
            if include_sources and "source_documents" in result:
                sources = []
                for doc in result["source_documents"]:
                    if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                        sources.append({
                            "source": doc.metadata["source"],
                            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                        })
                response["sources"] = sources
            
            logger.info(f"Pergunta respondida: '{question}'")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            return {
                "answer": f"Erro ao processar sua pergunta: {str(e)}",
                "sources": [],
                "success": False
            }
    
    def search_similar_documents(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Busca documentos similares sem gerar resposta
        
        Args:
            query: Consulta de busca
            k: Número de resultados
            
        Returns:
            Lista de documentos similares
        """
        try:
            documents = self.vector_store.similarity_search(query, k=k)
            
            results = []
            for doc in documents:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca de documentos similares: {str(e)}")
            return []
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o sistema
        
        Returns:
            Dicionário com informações do sistema
        """
        try:
            vector_info = self.vector_store.get_collection_info()
            
            info = {
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "vector_store": vector_info,
                "document_sources": self.vector_store.get_document_sources()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema: {str(e)}")
            return {}
    
    def reset_system(self) -> bool:
        """
        Reseta completamente o sistema
        
        Returns:
            True se resetado com sucesso
        """
        try:
            success = self.vector_store.reset_vector_store()
            if success:
                logger.info("Sistema RAG resetado com sucesso")
            return success
            
        except Exception as e:
            logger.error(f"Erro ao resetar sistema: {str(e)}")
            return False
    
    def update_model_settings(self, 
                            model_name: Optional[str] = None,
                            temperature: Optional[float] = None,
                            max_tokens: Optional[int] = None) -> bool:
        """
        Atualiza configurações do modelo
        
        Args:
            model_name: Novo nome do modelo
            temperature: Nova temperatura
            max_tokens: Novo máximo de tokens
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            if model_name:
                self.model_name = model_name
            if temperature is not None:
                self.temperature = temperature
            if max_tokens:
                self.max_tokens = max_tokens
            
            # Recriar modelo com novas configurações
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Recriar chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.vector_store.as_retriever(
                    search_kwargs={"k": 4}
                ),
                chain_type_kwargs={"prompt": self.prompt_template},
                return_source_documents=True
            )
            
            logger.info("Configurações do modelo atualizadas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações: {str(e)}")
            return False 