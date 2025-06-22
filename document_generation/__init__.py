"""
Módulo de Geração de Documentos Jurídicos
Integrado ao Sistema RAG Python

Este módulo adiciona capacidades de geração de documentos Word/PDF
usando IA e templates, mantendo a arquitetura existente do projeto.
"""

from .services.doc_generator import DocumentGenerator
from .services.pdf_converter import PDFConverter
from .models.document_models import DocRequest, DocResponse
from .api.document_api import DocumentAPI

__version__ = "1.0.0"
__description__ = "Geração de Documentos Jurídicos integrada ao RAG Python"

# Exportações principais
__all__ = [
    "DocumentGenerator",
    "PDFConverter", 
    "DocRequest",
    "DocResponse",
    "DocumentAPI"
] 