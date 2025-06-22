"""
Sistema RAG (Retrieval-Augmented Generation) em Python
Combina busca de documentos com geração de texto usando IA
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from document_loader import DocumentLoader
from vector_store import PGVectorStore  # Usaremos o PGVectorStore
from llm_providers import llm_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Erro de segurança para violações de isolamento de agente"""
    pass

class RAGSystem:
    """
    Sistema RAG que opera com um agente específico, usando PGVector para armazenamento.
    """
    def __init__(self, agent_id: str):
        if not agent_id or not isinstance(agent_id, str):
            raise ValueError("RAGSystem requer um agent_id válido.")
        
        self.agent_id = agent_id
        logger.info(f"Sistema RAG inicializado para o agente: {self.agent_id}")
        
        # Inicializar componentes
        self.document_loader = DocumentLoader()
        self.vector_store = PGVectorStore(agent_id=self.agent_id)
        
        # Configuração do text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def _validate_agent_access(self, context_docs: List[Document]) -> List[Document]:
        """Valida que todos os documentos pertencem ao agente atual"""
        validated_docs = []
        
        for doc in context_docs:
            # Verificar se o documento tem metadata de agente
            doc_agent_id = doc.metadata.get('agent_id')
            source_verified = doc.metadata.get('source_agent_verified', False)
            
            if doc_agent_id != self.agent_id or not source_verified:
                logger.error(f"🚨 VIOLAÇÃO DE SEGURANÇA: Documento de agente diferente detectado! Esperado: {self.agent_id}, Encontrado: {doc_agent_id}")
                raise SecurityError(f"Tentativa de acesso a documento de outro agente detectada")
            
            validated_docs.append(doc)
        
        logger.info(f"🔒 Validação de segurança: {len(validated_docs)} documentos validados para agente {self.agent_id}")
        return validated_docs

    def add_document(self, file_path: str):
        """Carrega, processa e armazena um documento para o agente."""
        try:
            logger.info(f"🔄 RAGSystem: Iniciando processamento de {file_path} para agente {self.agent_id}")
            
            # Carrega o conteúdo do arquivo
            documents = self.document_loader.load_document(file_path)
            if not documents:
                logger.warning(f"⚠️ RAGSystem: Nenhum conteúdo extraído de: {file_path}")
                return

            # Os documentos já vêm divididos em chunks do DocumentLoader
            logger.info(f"📄 RAGSystem: Documento dividido em {len(documents)} chunks.")

            # Gera embeddings e armazena no PGVector
            logger.info(f"🔗 RAGSystem: Iniciando armazenamento no vector store...")
            self.vector_store.add_documents(documents)
            logger.info(f"✅ RAGSystem: Documento '{file_path}' adicionado com sucesso ao agente {self.agent_id}.")

        except Exception as e:
            logger.error(f"❌ RAGSystem: Erro ao adicionar documento para o agente {self.agent_id}: {e}", exc_info=True)
            raise

    def add_document_from_text(self, content: str, source: str):
        """Processa e armazena um documento a partir de um texto e uma fonte."""
        try:
            # Cria um objeto Document do LangChain
            document = Document(page_content=content, metadata={"source": source})
            
            # Divide o documento em chunks
            chunks = self.text_splitter.split_documents([document])
            logger.info(f"Conteúdo de '{source}' dividido em {len(chunks)} chunks.")

            # Gera embeddings e armazena no PGVector
            self.vector_store.add_documents(chunks)
            logger.info(f"Conteúdo de '{source}' adicionado com sucesso ao agente {self.agent_id}.")

        except Exception as e:
            logger.error(f"Erro ao adicionar conteúdo de texto para o agente {self.agent_id}: {e}", exc_info=True)
            raise

    def get_relevant_context(self, query: str, k: int = 5) -> str:
        """Busca contexto relevante APENAS da base do agente atual."""
        try:
            logger.info(f"🔍 RAGSystem: Buscando contexto para agente {self.agent_id}")
            
            # Buscar documentos similares (já filtrados por agent_id no PGVectorStore)
            similar_docs = self.vector_store.similarity_search(query, k=k)
            
            # Validação adicional de segurança
            validated_docs = self._validate_agent_access(similar_docs)
            
            if not validated_docs:
                logger.warning(f"⚠️ RAGSystem: Nenhum contexto encontrado para agente {self.agent_id}")
                return ""
            
            # Combinar o conteúdo dos documentos
            context = "\n\n".join([doc.page_content for doc in validated_docs])
            logger.info(f"✅ RAGSystem: Contexto recuperado com {len(validated_docs)} chunks para agente {self.agent_id}")
            
            return context
            
        except Exception as e:
            logger.error(f"Erro ao buscar contexto para o agente {self.agent_id}: {e}")
            return ""

    def get_response(self, user_message: str, history: List[Dict[str, str]], system_prompt: str = "", temperature: float = 0.7, model: str = "gpt-4o-mini") -> str:
        """Gera uma resposta usando RAG ISOLADO para o agente."""
        try:
            if not llm_manager.get_active_provider():
                logger.error("Nenhum provedor de LLM está configurado. Verifique as variáveis de ambiente (ex: OPENAI_API_KEY).")
                return "Erro de configuração: Nenhum provedor de LLM foi configurado. Por favor, adicione uma chave de API nas configurações."

            context = self.get_relevant_context(user_message)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if context:
                context_message = f"Use o seguinte contexto para responder à pergunta do usuário:\n\n---\n{context}\n---"
                if messages and messages[0]['role'] == 'system':
                    messages[0]['content'] += "\n\n" + context_message
                else:
                    messages.insert(0, {"role": "system", "content": context_message})

            if history:
                messages.extend(history)
            
            messages.append({"role": "user", "content": user_message})

            response_text = llm_manager.generate_response(
                messages,
                model=model,
                temperature=temperature
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta para o agente {self.agent_id}: {e}", exc_info=True)
            error_str = str(e).lower()
            if 'authentication' in error_str or 'api key' in error_str or 'api-key' in error_str:
                return "Erro de autenticação: A chave da API é inválida ou está faltando. Verifique suas credenciais."
            return "Desculpe, ocorreu um erro ao processar sua solicitação."

    def get_multi_response(self, user_message: str, context: str, history: List[Dict[str, str]], system_prompt: str, temperature: float, providers: List[str]) -> Dict[str, Any]:
        """Gera respostas de múltiplos LLMs usando o contexto RAG ISOLADO."""
        responses = {}
        
        for provider in providers:
            try:
                if context:
                    enhanced_prompt = f"{system_prompt}\n\nContexto relevante:\n{context}\n\nPergunta do usuário: {user_message}"
                else:
                    enhanced_prompt = f"{system_prompt}\n\nPergunta do usuário: {user_message}"
                
                llm = llm_manager.get_llm_instance(provider=provider, temperature=temperature)
                response = llm.invoke(enhanced_prompt)
                
                responses[provider] = {
                    'content': response.content if hasattr(response, 'content') else str(response),
                    'model': llm_manager.get_model_name(provider),
                    'usage': {}
                }
                
            except Exception as e:
                logger.error(f"Erro ao gerar resposta com {provider} para agente {self.agent_id}: {e}")
                responses[provider] = {
                    'content': f"Erro ao processar com {provider}: {str(e)}",
                    'model': 'N/A',
                    'usage': {}
                }
        
        return responses 