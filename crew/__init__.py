"""
Módulo CrewAI para Orquestração de Agentes
Integrado ao Sistema RAG Python v1.5.0

Este módulo adiciona capacidades de orquestração avançada de agentes
usando CrewAI, mantendo compatibilidade com a arquitetura existente.
"""

from .agents import (
    RetrievalAgent,
    SummarizationAgent, 
    DocumentGenerationAgent,
    LegalAnalysisAgent,
    PrivacyComplianceAgent
)
from .pipelines import (
    LegalDocumentPipeline,
    ContractGenerationPipeline,
    LegalResearchPipeline,
    CompliancePipeline
)
from .orchestrator import CrewOrchestrator

__version__ = "1.0.0"
__description__ = "Orquestração de Agentes com CrewAI para RAG Python"

# Exportações principais
__all__ = [
    "RetrievalAgent",
    "SummarizationAgent", 
    "DocumentGenerationAgent",
    "LegalAnalysisAgent",
    "PrivacyComplianceAgent",
    "LegalDocumentPipeline",
    "ContractGenerationPipeline", 
    "LegalResearchPipeline",
    "CompliancePipeline",
    "CrewOrchestrator"
] 