"""
Agentes CrewAI especializados para ambiente jurídico
Integrados com o sistema RAG Python existente
"""

import logging
from typing import Dict, Any, List, Optional
from crewai import Agent, Task
from langchain.tools import Tool

# Importações do sistema existente
from rag_system import RAGSystem
from agent_system import Agent as RAGAgent
from privacy_system import PrivacyCompliance
from llm_providers import llm_manager

logger = logging.getLogger(__name__)

class BaseRAGCrewAgent(Agent):
    """Classe base para agentes CrewAI integrados com RAG"""
    
    def __init__(self, agent_id: str, **kwargs):
        self.agent_id = agent_id
        self.rag_system = RAGSystem(agent_id=agent_id)
        self.privacy_manager = PrivacyCompliance()
        super().__init__(**kwargs)
    
    def get_rag_tool(self) -> Tool:
        """Ferramenta para busca RAG"""
        def rag_search(query: str) -> str:
            try:
                response = self.rag_system.query(query)
                return response.get('answer', 'Nenhuma informação encontrada')
            except Exception as e:
                logger.error(f"Erro na busca RAG: {e}")
                return f"Erro na busca: {str(e)}"
        
        return Tool(
            name="rag_search",
            description="Busca informações na base de conhecimento do agente",
            func=rag_search
        )

class RetrievalAgent(BaseRAGCrewAgent):
    """Agente especializado em recuperação de informações"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role="Especialista em Recuperação de Informações",
            goal="Encontrar e recuperar informações relevantes da base de conhecimento",
            backstory="""Você é um especialista em busca e recuperação de informações jurídicas.
            Sua missão é encontrar os documentos e trechos mais relevantes para responder
            às consultas dos usuários com precisão e completude.""",
            tools=[self.get_rag_tool()],
            verbose=True
        )

class SummarizationAgent(BaseRAGCrewAgent):
    """Agente especializado em sumarização"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role="Especialista em Sumarização",
            goal="Criar resumos claros e objetivos de documentos e informações",
            backstory="""Você é um especialista em análise e síntese de informações jurídicas.
            Sua especialidade é transformar grandes volumes de texto em resumos
            claros, objetivos e acionáveis.""",
            tools=[self.get_rag_tool()],
            verbose=True
        )

class DocumentGenerationAgent(BaseRAGCrewAgent):
    """Agente especializado em geração de documentos"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role="Especialista em Geração de Documentos",
            goal="Gerar documentos jurídicos profissionais e personalizados",
            backstory="""Você é um especialista em redação jurídica e geração de documentos.
            Sua missão é criar documentos profissionais, precisos e adequados
            às necessidades específicas de cada caso.""",
            tools=[self.get_rag_tool(), self.get_document_tool()],
            verbose=True
        )
    
    def get_document_tool(self) -> Tool:
        """Ferramenta para geração de documentos"""
        def generate_document(template_type: str, variables: str) -> str:
            try:
                # Integração com sistema de documentos (a ser implementado)
                return f"Documento {template_type} gerado com sucesso"
            except Exception as e:
                return f"Erro na geração: {str(e)}"
        
        return Tool(
            name="generate_document",
            description="Gera documentos a partir de templates",
            func=generate_document
        )

class LegalAnalysisAgent(BaseRAGCrewAgent):
    """Agente especializado em análise jurídica"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role="Especialista em Análise Jurídica",
            goal="Realizar análises jurídicas profundas e fundamentadas",
            backstory="""Você é um jurista experiente especializado em análise de casos,
            precedentes e legislação. Sua missão é fornecer análises jurídicas
            sólidas e bem fundamentadas.""",
            tools=[self.get_rag_tool(), self.get_legal_analysis_tool()],
            verbose=True
        )
    
    def get_legal_analysis_tool(self) -> Tool:
        """Ferramenta para análise jurídica"""
        def legal_analysis(case_data: str) -> str:
            try:
                # Análise usando RAG + LLM
                context = self.rag_system.get_relevant_context(case_data)
                analysis_prompt = f"""
                Analise o seguinte caso jurídico com base no contexto fornecido:
                
                Caso: {case_data}
                Contexto: {context}
                
                Forneça uma análise jurídica completa incluindo:
                1. Fundamentos legais aplicáveis
                2. Precedentes relevantes
                3. Riscos e oportunidades
                4. Recomendações estratégicas
                """
                
                response = llm_manager.get_response(
                    analysis_prompt,
                    temperature=0.3,
                    max_tokens=2000
                )
                return response
            except Exception as e:
                return f"Erro na análise: {str(e)}"
        
        return Tool(
            name="legal_analysis",
            description="Realiza análise jurídica detalhada",
            func=legal_analysis
        )

class PrivacyComplianceAgent(BaseRAGCrewAgent):
    """Agente especializado em compliance de privacidade"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role="Especialista em Compliance de Privacidade",
            goal="Garantir conformidade com LGPD e regulamentações de privacidade",
            backstory="""Você é um especialista em proteção de dados e compliance LGPD.
            Sua missão é garantir que todos os processos estejam em conformidade
            com as regulamentações de privacidade e proteção de dados.""",
            tools=[self.get_rag_tool(), self.get_privacy_tool()],
            verbose=True
        )
    
    def get_privacy_tool(self) -> Tool:
        """Ferramenta para análise de privacidade"""
        def privacy_check(content: str) -> str:
            try:
                # Usar sistema de privacidade existente
                result = self.privacy_manager.detect_personal_data_only(content)
                
                if result['has_personal_data']:
                    return f"""
                    ⚠️ DADOS PESSOAIS DETECTADOS:
                    - Tipos: {', '.join(result['detected_types'])}
                    - Categoria: {result['data_category']}
                    - Ocorrências: {result['total_occurrences']}
                    
                    Recomendações de compliance necessárias.
                    """
                else:
                    return "✅ Nenhum dado pessoal detectado. Conteúdo aprovado."
                    
            except Exception as e:
                return f"Erro na verificação: {str(e)}"
        
        return Tool(
            name="privacy_check",
            description="Verifica conformidade LGPD e detecta dados pessoais",
            func=privacy_check
        )

# Função helper para criar agentes
def create_agent_crew(agent_id: str, agent_types: List[str]) -> List[BaseRAGCrewAgent]:
    """Cria uma equipe de agentes CrewAI"""
    agents = []
    
    agent_classes = {
        'retrieval': RetrievalAgent,
        'summarization': SummarizationAgent,
        'document_generation': DocumentGenerationAgent,
        'legal_analysis': LegalAnalysisAgent,
        'privacy_compliance': PrivacyComplianceAgent
    }
    
    for agent_type in agent_types:
        if agent_type in agent_classes:
            agent = agent_classes[agent_type](agent_id)
            agents.append(agent)
            logger.info(f"Agente {agent_type} criado para {agent_id}")
    
    return agents 