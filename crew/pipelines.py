"""
Pipelines de Workflow CrewAI para Cenários Jurídicos
Orquestração de agentes para casos específicos
"""

import logging
from typing import Dict, Any, List
from crewai import Crew, Task, Process
from .agents import (
    RetrievalAgent,
    SummarizationAgent,
    DocumentGenerationAgent,
    LegalAnalysisAgent,
    PrivacyComplianceAgent
)

logger = logging.getLogger(__name__)

class BasePipeline:
    """Classe base para pipelines CrewAI"""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.agents = []
        self.tasks = []
        self.crew = None
    
    def create_crew(self) -> Crew:
        """Cria o crew com agentes e tarefas"""
        self.crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        return self.crew
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Executa o pipeline"""
        try:
            if not self.crew:
                self.create_crew()
            
            result = self.crew.kickoff(inputs)
            
            logger.info(f"Pipeline {self.name} executado com sucesso")
            return {
                'success': True,
                'result': result,
                'pipeline': self.name,
                'agent_id': self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Erro no pipeline {self.name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'pipeline': self.name,
                'agent_id': self.agent_id
            }

class LegalDocumentPipeline(BasePipeline):
    """Pipeline para geração de documentos jurídicos"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "LegalDocumentGeneration")
        
        # Criar agentes
        self.retrieval_agent = RetrievalAgent(agent_id)
        self.legal_agent = LegalAnalysisAgent(agent_id)
        self.doc_agent = DocumentGenerationAgent(agent_id)
        self.privacy_agent = PrivacyComplianceAgent(agent_id)
        
        self.agents = [
            self.retrieval_agent,
            self.legal_agent,
            self.doc_agent,
            self.privacy_agent
        ]
        
        # Criar tarefas
        self.create_tasks()
    
    def create_tasks(self):
        """Cria as tarefas do pipeline"""
        
        # Tarefa 1: Buscar informações relevantes
        retrieval_task = Task(
            description="""
            Busque informações relevantes na base de conhecimento sobre:
            - Tipo de documento solicitado: {document_type}
            - Contexto específico: {context}
            - Partes envolvidas: {parties}
            
            Retorne as informações mais relevantes e atualizadas.
            """,
            agent=self.retrieval_agent,
            expected_output="Informações detalhadas e contextualizadas sobre o documento solicitado"
        )
        
        # Tarefa 2: Análise jurídica
        analysis_task = Task(
            description="""
            Com base nas informações recuperadas, realize uma análise jurídica completa:
            - Identifique fundamentos legais aplicáveis
            - Analise precedentes relevantes
            - Avalie riscos e oportunidades
            - Sugira estratégias e cláusulas apropriadas
            
            Contexto: {context}
            Informações recuperadas: {retrieval_result}
            """,
            agent=self.legal_agent,
            expected_output="Análise jurídica fundamentada com recomendações específicas"
        )
        
        # Tarefa 3: Geração do documento
        generation_task = Task(
            description="""
            Gere um documento jurídico profissional com base na análise realizada:
            - Tipo: {document_type}
            - Partes: {parties}
            - Cláusulas específicas baseadas na análise
            - Formatação profissional
            
            Análise jurídica: {analysis_result}
            Variáveis: {variables}
            """,
            agent=self.doc_agent,
            expected_output="Documento jurídico completo e profissional"
        )
        
        # Tarefa 4: Verificação de compliance
        compliance_task = Task(
            description="""
            Verifique o documento gerado quanto à conformidade LGPD:
            - Detecte dados pessoais
            - Avalie riscos de privacidade
            - Sugira ajustes se necessário
            
            Documento: {document_result}
            """,
            agent=self.privacy_agent,
            expected_output="Relatório de compliance com aprovação ou sugestões de ajuste"
        )
        
        self.tasks = [retrieval_task, analysis_task, generation_task, compliance_task]

class ContractGenerationPipeline(BasePipeline):
    """Pipeline especializado para geração de contratos"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "ContractGeneration")
        
        # Agentes especializados em contratos
        self.retrieval_agent = RetrievalAgent(agent_id)
        self.legal_agent = LegalAnalysisAgent(agent_id)
        self.doc_agent = DocumentGenerationAgent(agent_id)
        
        self.agents = [self.retrieval_agent, self.legal_agent, self.doc_agent]
        self.create_contract_tasks()
    
    def create_contract_tasks(self):
        """Tarefas específicas para contratos"""
        
        # Busca de templates e precedentes
        template_task = Task(
            description="""
            Busque templates e precedentes para o tipo de contrato:
            - Tipo de contrato: {contract_type}
            - Setor: {business_sector}
            - Valor envolvido: {contract_value}
            
            Encontre os melhores modelos e cláusulas padrão.
            """,
            agent=self.retrieval_agent,
            expected_output="Templates e cláusulas padrão relevantes"
        )
        
        # Análise de riscos contratuais
        risk_analysis_task = Task(
            description="""
            Analise os riscos específicos do contrato:
            - Riscos comerciais
            - Riscos legais
            - Cláusulas de proteção necessárias
            - Garantias e penalidades
            
            Contexto: {contract_context}
            Templates encontrados: {template_result}
            """,
            agent=self.legal_agent,
            expected_output="Análise de riscos com cláusulas de proteção recomendadas"
        )
        
        # Geração do contrato final
        contract_generation_task = Task(
            description="""
            Gere um contrato completo e balanceado:
            - Incorpore as cláusulas de proteção identificadas
            - Use linguagem jurídica apropriada
            - Inclua todas as especificações técnicas
            - Formate profissionalmente
            
            Análise de riscos: {risk_analysis_result}
            Especificações: {contract_specs}
            """,
            agent=self.doc_agent,
            expected_output="Contrato completo pronto para revisão e assinatura"
        )
        
        self.tasks = [template_task, risk_analysis_task, contract_generation_task]

class LegalResearchPipeline(BasePipeline):
    """Pipeline para pesquisa jurídica avançada"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "LegalResearch")
        
        self.retrieval_agent = RetrievalAgent(agent_id)
        self.legal_agent = LegalAnalysisAgent(agent_id)
        self.summary_agent = SummarizationAgent(agent_id)
        
        self.agents = [self.retrieval_agent, self.legal_agent, self.summary_agent]
        self.create_research_tasks()
    
    def create_research_tasks(self):
        """Tarefas para pesquisa jurídica"""
        
        # Busca abrangente
        comprehensive_search_task = Task(
            description="""
            Realize uma busca abrangente sobre o tema:
            - Tema principal: {research_topic}
            - Subtemas relacionados: {subtopics}
            - Período de interesse: {time_period}
            
            Busque legislação, jurisprudência, doutrina e precedentes.
            """,
            agent=self.retrieval_agent,
            expected_output="Conjunto abrangente de informações jurídicas sobre o tema"
        )
        
        # Análise jurídica profunda
        deep_analysis_task = Task(
            description="""
            Realize análise jurídica profunda dos materiais encontrados:
            - Identifique tendências jurisprudenciais
            - Analise mudanças legislativas
            - Avalie impactos práticos
            - Identifique lacunas e oportunidades
            
            Materiais encontrados: {search_result}
            """,
            agent=self.legal_agent,
            expected_output="Análise jurídica profunda com insights estratégicos"
        )
        
        # Síntese executiva
        synthesis_task = Task(
            description="""
            Crie uma síntese executiva da pesquisa:
            - Resumo dos principais achados
            - Conclusões práticas
            - Recomendações estratégicas
            - Próximos passos sugeridos
            
            Análise completa: {analysis_result}
            """,
            agent=self.summary_agent,
            expected_output="Síntese executiva clara e acionável"
        )
        
        self.tasks = [comprehensive_search_task, deep_analysis_task, synthesis_task]

class CompliancePipeline(BasePipeline):
    """Pipeline para análise de compliance"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "ComplianceAnalysis")
        
        self.retrieval_agent = RetrievalAgent(agent_id)
        self.privacy_agent = PrivacyComplianceAgent(agent_id)
        self.legal_agent = LegalAnalysisAgent(agent_id)
        
        self.agents = [self.retrieval_agent, self.privacy_agent, self.legal_agent]
        self.create_compliance_tasks()
    
    def create_compliance_tasks(self):
        """Tarefas para análise de compliance"""
        
        # Busca de regulamentações
        regulation_search_task = Task(
            description="""
            Busque todas as regulamentações aplicáveis:
            - Setor: {business_sector}
            - Tipo de atividade: {activity_type}
            - Jurisdição: {jurisdiction}
            
            Inclua LGPD, regulamentações setoriais e normas aplicáveis.
            """,
            agent=self.retrieval_agent,
            expected_output="Lista completa de regulamentações aplicáveis"
        )
        
        # Análise de privacidade
        privacy_analysis_task = Task(
            description="""
            Analise aspectos de privacidade e proteção de dados:
            - Tipos de dados coletados: {data_types}
            - Finalidades de processamento: {processing_purposes}
            - Medidas de segurança: {security_measures}
            
            Regulamentações encontradas: {regulation_result}
            """,
            agent=self.privacy_agent,
            expected_output="Análise de conformidade LGPD com recomendações"
        )
        
        # Avaliação geral de compliance
        compliance_assessment_task = Task(
            description="""
            Realize avaliação geral de compliance:
            - Identifique gaps de conformidade
            - Avalie riscos regulatórios
            - Sugira plano de adequação
            - Priorize ações necessárias
            
            Análise de privacidade: {privacy_result}
            Contexto organizacional: {organization_context}
            """,
            agent=self.legal_agent,
            expected_output="Relatório completo de compliance com plano de ação"
        )
        
        self.tasks = [regulation_search_task, privacy_analysis_task, compliance_assessment_task]

# Factory function para criar pipelines
def create_pipeline(pipeline_type: str, agent_id: str) -> BasePipeline:
    """Factory para criar pipelines"""
    
    pipelines = {
        'legal_document': LegalDocumentPipeline,
        'contract_generation': ContractGenerationPipeline,
        'legal_research': LegalResearchPipeline,
        'compliance': CompliancePipeline
    }
    
    if pipeline_type not in pipelines:
        raise ValueError(f"Tipo de pipeline inválido: {pipeline_type}")
    
    return pipelines[pipeline_type](agent_id) 