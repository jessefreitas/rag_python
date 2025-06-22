"""
Módulo de Geração de Documentos Jurídicos
Integrado ao Sistema RAG Python

Este módulo adiciona capacidades de geração de documentos Word/PDF
usando IA e templates, mantendo a arquitetura existente do projeto.
"""

from .services.doc_generator import DocumentGenerator, document_generator
from .services.pdf_converter import PDFConverter, pdf_converter
from .models.document_models import DocRequest, DocResponse, DocumentTemplate

__version__ = "1.5.0"
__description__ = "Geração de Documentos Jurídicos integrada ao RAG Python com CrewAI"

# Exportações principais
__all__ = [
    "DocumentGenerator",
    "document_generator",
    "PDFConverter", 
    "pdf_converter",
    "DocRequest",
    "DocResponse",
    "DocumentTemplate"
] 