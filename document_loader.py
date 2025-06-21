"""
Módulo para carregamento e processamento de documentos
Suporta PDF, DOCX, TXT e páginas web
"""

import os
import requests
from typing import List, Dict, Any
from pathlib import Path
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    WebBaseLoader
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    """Classe para carregar e processar diferentes tipos de documentos"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Carrega um documento baseado na extensão do arquivo
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Lista de chunks do documento
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                loader = Docx2txtLoader(str(file_path))
            elif file_path.suffix.lower() == '.txt':
                loader = TextLoader(str(file_path), encoding='utf-8')
            else:
                raise ValueError(f"Tipo de arquivo não suportado: {file_path.suffix}")
            
            documents = loader.load()
            logger.info(f"Carregados {len(documents)} documentos de {file_path}")
            
            # Adicionar metadados
            for doc in documents:
                doc.metadata['source'] = str(file_path)
                doc.metadata['file_type'] = file_path.suffix.lower()
            
            return self.split_documents(documents)
            
        except Exception as e:
            logger.error(f"Erro ao carregar {file_path}: {str(e)}")
            raise
    
    def load_web_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Carrega conteúdo de uma página web
        
        Args:
            url: URL da página web
            
        Returns:
            Lista de chunks do conteúdo
        """
        try:
            loader = WebBaseLoader(url)
            documents = loader.load()
            
            # Adicionar metadados
            for doc in documents:
                doc.metadata['source'] = url
                doc.metadata['file_type'] = 'web'
            
            logger.info(f"Carregados {len(documents)} documentos da web: {url}")
            return self.split_documents(documents)
            
        except Exception as e:
            logger.error(f"Erro ao carregar página web {url}: {str(e)}")
            raise
    
    def split_documents(self, documents: List[Any]) -> List[Dict[str, Any]]:
        """
        Divide documentos em chunks menores
        
        Args:
            documents: Lista de documentos LangChain
            
        Returns:
            Lista de chunks processados
        """
        try:
            splits = self.text_splitter.split_documents(documents)
            logger.info(f"Documentos divididos em {len(splits)} chunks")
            return splits
        except Exception as e:
            logger.error(f"Erro ao dividir documentos: {str(e)}")
            raise
    
    def load_documents_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Carrega todos os documentos suportados de um diretório
        
        Args:
            directory_path: Caminho para o diretório
            
        Returns:
            Lista de todos os chunks dos documentos
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory_path}")
        
        all_chunks = []
        supported_extensions = {'.pdf', '.docx', '.doc', '.txt'}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    chunks = self.load_document(str(file_path))
                    all_chunks.extend(chunks)
                    logger.info(f"Processado: {file_path}")
                except Exception as e:
                    logger.warning(f"Erro ao processar {file_path}: {str(e)}")
                    continue
        
        logger.info(f"Total de chunks carregados: {len(all_chunks)}")
        return all_chunks
    
    def validate_url(self, url: str) -> bool:
        """
        Valida se uma URL é acessível
        
        Args:
            url: URL para validar
            
        Returns:
            True se a URL é válida e acessível
        """
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False 