"""
Sistema RAG (Retrieval-Augmented Generation) em Python
Combina busca de documentos com geração de texto usando IA
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

from document_loader import DocumentLoader
from vector_store import VectorStore
from llm_providers import llm_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    """Sistema RAG principal que combina busca de documentos com geração de texto"""
    
    def __init__(self, 
                 vector_db_path: str = "vector_db",
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.7,
                 max_tokens: int = 1000,
                 provider: str = "openai"):
        """
        Inicializa o sistema RAG
        
        Args:
            vector_db_path: Caminho para o banco de vetores
            model_name: Nome do modelo de IA
            temperature: Temperatura para geração de texto
            max_tokens: Máximo de tokens na resposta
            provider: Provedor de IA (openai, openrouter, gemini)
        """
        self.vector_db_path = vector_db_path
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore(
            collection_name=f"agent_{Path(vector_db_path).name}",
            persist_directory=self.vector_db_path
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        # Configurar provedor de IA
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Verificar se o provedor está disponível
        if provider not in llm_manager.list_available_providers():
            available = llm_manager.list_available_providers()
            if not available:
                raise ValueError("Nenhum provedor de IA configurado. Configure OPENAI_API_KEY, OPENROUTER_API_KEY ou GOOGLE_GEMINI_API_KEY")
            else:
                logger.warning(f"Provedor '{provider}' não disponível. Usando '{available[0]}'")
                self.provider = available[0]
        
        # Definir provedor ativo
        llm_manager.set_active_provider(self.provider)
        
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
        self.qa_chain = self._create_qa_chain()
        
        logger.info(f"Sistema RAG inicializado com provedor: {self.provider}, modelo: {self.model_name}")
    
    def _create_qa_chain(self):
        """Cria a chain de QA usando o provedor configurado"""
        try:
            # Usar o gerenciador de provedores para gerar respostas
            def llm_generate(prompt: str) -> str:
                messages = [{"role": "user", "content": prompt}]
                return llm_manager.generate_response(
                    messages,
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            
            # Criar chain customizada
            from langchain.chains import LLMChain
            from langchain.schema import BaseRetriever
            
            class CustomRetrievalQA:
                def __init__(self, retriever, llm_chain):
                    self.retriever = retriever
                    self.llm_chain = llm_chain
                
                def __call__(self, question: str):
                    # Buscar documentos relevantes
                    docs = self.retriever.get_relevant_documents(question)
                    context = "\n\n".join([doc.page_content for doc in docs])
                    
                    # Gerar resposta
                    response = llm_generate(self.prompt_template.format(
                        context=context,
                        question=question
                    ))
                    
                    return {
                        "result": response,
                        "source_documents": docs
                    }
            
            retriever = self.vector_store.vector_store.as_retriever(search_kwargs={"k": 4})
            return CustomRetrievalQA(retriever, None)
            
        except Exception as e:
            logger.error(f"Erro ao criar chain de QA: {e}")
            raise
    
    def load_documents(self, 
                      file_paths: Optional[List[str]] = None,
                      directory_path: Optional[str] = None,
                      text: Optional[str] = None) -> bool:
        """
        Carrega documentos no sistema RAG
        
        Args:
            file_paths: Lista de caminhos de arquivos
            directory_path: Caminho do diretório
            text: Texto direto
            
        Returns:
            bool: True se documentos foram carregados com sucesso
        """
        try:
            documents = []
            
            # Carregar de arquivos específicos
            if file_paths:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        doc = self.document_loader.load_file(file_path)
                        if doc:
                            documents.extend(doc)
                            logger.info(f"Documento carregado: {file_path}")
                    else:
                        logger.warning(f"Arquivo não encontrado: {file_path}")
            
            # Carregar de diretório
            if directory_path:
                if os.path.exists(directory_path):
                    docs = self.document_loader.load_directory(directory_path)
                    documents.extend(docs)
                    logger.info(f"Documentos carregados do diretório: {directory_path}")
                else:
                    logger.warning(f"Diretório não encontrado: {directory_path}")
            
            # Carregar texto direto
            if text:
                from langchain.schema import Document
                documents.append(Document(page_content=text, metadata={"source": "text_input"}))
                logger.info("Texto direto carregado")
            
            if not documents:
                logger.warning("Nenhum documento foi carregado")
                return False
            
            # Dividir documentos em chunks
            texts = self.text_splitter.split_documents(documents)
            logger.info(f"Documentos divididos em {len(texts)} chunks")
            
            # Adicionar ao vector store
            self.vector_store.add_documents(texts)
            logger.info("Documentos adicionados ao vector store")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar documentos: {e}")
            return False
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Faz uma pergunta ao sistema RAG
        
        Args:
            question: Pergunta a ser respondida
            
        Returns:
            Dict com resposta e documentos fonte
        """
        try:
            if not self.qa_chain:
                raise ValueError("Chain de QA não inicializada")
            
            result = self.qa_chain(question)
            
            return {
                "answer": result["result"],
                "sources": [doc.metadata.get("source", "Unknown") for doc in result["source_documents"]],
                "documents": result["source_documents"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            return {
                "answer": f"Erro ao processar sua pergunta: {str(e)}",
                "sources": [],
                "documents": []
            }
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca documentos similares
        
        Args:
            query: Consulta de busca
            k: Número de resultados
            
        Returns:
            Lista de documentos similares
        """
        try:
            docs = self.vector_store.vector_store.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 0.0  # ChromaDB não retorna scores por padrão
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca de documentos: {e}")
            return []
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o sistema"""
        return {
            "provider": self.provider,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "vector_db_path": self.vector_db_path,
            "available_providers": llm_manager.list_available_providers(),
            "provider_info": llm_manager.get_provider_info()
        }
    
    def update_model_settings(self, 
                            model_name: Optional[str] = None,
                            temperature: Optional[float] = None,
                            max_tokens: Optional[int] = None,
                            provider: Optional[str] = None) -> bool:
        """
        Atualiza configurações do modelo
        
        Args:
            model_name: Novo nome do modelo
            temperature: Nova temperatura
            max_tokens: Novo máximo de tokens
            provider: Novo provedor
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            if provider and provider != self.provider:
                if provider in llm_manager.list_available_providers():
                    self.provider = provider
                    llm_manager.set_active_provider(provider)
                else:
                    logger.error(f"Provedor '{provider}' não disponível")
                    return False
            
            if model_name:
                self.model_name = model_name
            if temperature is not None:
                self.temperature = temperature
            if max_tokens:
                self.max_tokens = max_tokens
            
            # Recriar chain com novas configurações
            self.qa_chain = self._create_qa_chain()
            
            logger.info("Configurações do modelo atualizadas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações: {str(e)}")
            return False 