"""
Sistema de Agentes de IA integrado com RAG
Permite criar diferentes tipos de agentes que usam o RAG como base de conhecimento
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import asyncio
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.messages import SystemMessage

from rag_system import RAGSystem
from ragflow_client import RAGFlowRAGSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Resposta do agente"""
    content: str
    actions_taken: List[str] = field(default_factory=list)
    confidence: float = 0.0
    sources: List[Dict] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

# Definição de uma classe de configuração simples para manter a compatibilidade
class AgentConfig:
    def __init__(self, agent_id=None, agent_name=None, model_name="gpt-3.5-turbo", temperature=0.7, system_prompt="Você é um assistente prestativo.", memory=True, max_iterations=5, tools=None):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.memory = memory
        self.max_iterations = max_iterations
        self.tools = tools if tools is not None else ["rag_query", "search_documents"]

class BaseAgent:
    """Classe base para todos os agentes"""

    def __init__(self, config: AgentConfig, rag_system=None):
        """
        Inicializa o agente base
        
        Args:
            config: Configuração do agente
            rag_system: Sistema RAG para consulta de conhecimento
        """
        self.config = config
        self.rag_system = rag_system
        self.llm = ChatOpenAI(
            model_name=config.model_name,
            temperature=config.temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        ) if config.memory else None
        
        # Histórico de ações
        self.action_history = []
        
        # Inicializar ferramentas
        self.tools = self._create_tools()
        
        # Inicializar agente LangChain
        self.agent = self._create_agent()

    def _create_tools(self) -> List[Tool]:
        """Cria as ferramentas disponíveis para o agente"""
        tools = []
        
        # Ferramenta de consulta RAG
        if self.rag_system and "rag_query" in self.config.tools:
            tools.append(Tool(
                name="rag_query",
                description="Consulta o sistema RAG para obter informações baseadas em documentos",
                func=self._rag_query_tool
            ))
        
        # Ferramenta de busca de documentos
        if self.rag_system and "search_documents" in self.config.tools:
            tools.append(Tool(
                name="search_documents",
                description="Busca documentos similares no sistema RAG",
                func=self._search_documents_tool
            ))
        
        return tools

    def _create_agent(self):
        """Cria o executor do agente LangChain"""
        try:
            return initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                memory=self.memory,
                verbose=True,
                max_iterations=self.config.max_iterations,
                handle_parsing_errors=True
            )
        except Exception as e:
            logging.error(f"Erro ao criar o agente: {e}")
            return None

    def _rag_query_tool(self, query: str) -> str:
        """Executa a consulta no sistema RAG e retorna a resposta como string."""
        try:
            result = self.rag_system.query(query)
            if result and result.get("success"):
                return result.get("answer", "Não foi possível obter uma resposta.")
            else:
                return f"Ocorreu um erro ao consultar a base de conhecimento: {result.get('answer')}"
        except Exception as e:
            logging.error(f"Erro na ferramenta RAG: {e}")
            return f"Exceção ao consultar a base de conhecimento: {str(e)}"

    def _search_documents_tool(self, query: str) -> str:
        """Executa a busca por documentos similares e retorna um resumo em string."""
        try:
            results = self.rag_system.search_similar_documents(query)
            if not results:
                return "Nenhum documento similar encontrado."
            
            # Formatar a saída como uma string simples
            formatted_results = "\n\n---\n\n".join(
                [f"Fonte: {doc.get('metadata', {}).get('source', 'N/A')}\nConteúdo: {doc.get('content', '')}" for doc in results]
            )
            return f"Encontrei {len(results)} documentos relevantes:\n\n{formatted_results}"
        except Exception as e:
            logging.error(f"Erro na ferramenta de busca: {e}")
            return f"Exceção ao buscar documentos: {str(e)}"
    
    def run(self, user_input: str) -> str:
        """
        Executa o agente com a entrada do usuário.

        Args:
            user_input (str): A entrada do usuário.

        Returns:
            str: A resposta do agente.
        """
        # Adicionar prompt do sistema se ainda não houver mensagens
        if self.memory and not self.memory.chat_memory.messages:
            # Adicionar prompt do sistema
            self.memory.chat_memory.add_message(SystemMessage(content=self.config.system_prompt))
        
        try:
            # Usar .invoke() que é o método atual e espera um dicionário.
            result = self.agent.invoke({"input": user_input})
            
            # O resultado de .invoke() é um dicionário, a resposta final está na chave 'output'
            return result.get('output', "Desculpe, não consegui encontrar uma resposta.")

        except Exception as e:
            logging.error(f"Erro ao executar o agente: {e}")
            # Tenta obter o erro de análise de saída
            if "Could not parse LLM output" in str(e):
                error_message = str(e).split("`")[1]
                logging.error(f"Erro de Análise: {error_message}")
                return f"Desculpe, tive um problema ao processar a resposta. Tente novamente. (Erro: {error_message})"
            return f"Ocorreu um erro: {e}"

class ConversationalAgent(BaseAgent):
    """Agente conversacional que usa RAG para respostas baseadas em documentos"""
    
    def __init__(self, rag_system=None):
        config = AgentConfig(
            name="Conversational Agent",
            description="Agente conversacional que usa RAG para respostas informadas",
            system_prompt="""Você é um assistente conversacional inteligente que usa um sistema RAG 
            para fornecer respostas baseadas em documentos específicos. Sempre que possível, 
            consulte o sistema RAG para obter informações precisas e atualizadas. 
            Seja amigável, útil e forneça respostas claras e concisas.""",
            tools=["rag_query", "search_documents"],
            memory=True,
            temperature=0.7
        )
        super().__init__(config, rag_system)

class ResearchAgent(BaseAgent):
    """Agente de pesquisa que analisa documentos e extrai insights"""
    
    def __init__(self, rag_system=None):
        config = AgentConfig(
            name="Research Agent",
            description="Agente especializado em pesquisa e análise de documentos",
            system_prompt="""Você é um agente de pesquisa especializado em analisar documentos 
            e extrair insights valiosos. Use o sistema RAG para buscar informações relevantes 
            e forneça análises detalhadas, resumos e recomendações baseadas nos documentos disponíveis.""",
            tools=["rag_query", "search_documents"],
            memory=True,
            temperature=0.3,
            max_iterations=8
        )
        super().__init__(config, rag_system)
    
    def analyze_documents(self, topic: str) -> AgentResponse:
        """
        Analisa documentos sobre um tópico específico
        
        Args:
            topic: Tópico para análise
            
        Returns:
            Análise dos documentos
        """
        try:
            # Buscar documentos relacionados
            documents = self.rag_system.search_similar_documents(topic, k=5)
            
            if not documents:
                return AgentResponse(
                    content=f"Nenhum documento encontrado sobre '{topic}'",
                    confidence=0.0
                )
            
            # Criar prompt de análise
            analysis_prompt = f"""
            Analise os seguintes documentos sobre '{topic}' e forneça:
            1. Resumo dos principais pontos
            2. Insights e descobertas importantes
            3. Recomendações baseadas na análise
            4. Gaps de informação identificados
            
            Documentos encontrados: {len(documents)}
            """
            
            # Processar análise
            response = self.process(analysis_prompt)
            
            # Adicionar metadados da análise
            response.metadata.update({
                "topic": topic,
                "documents_analyzed": len(documents),
                "analysis_type": "document_research"
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na análise de documentos: {str(e)}")
            return AgentResponse(
                content=f"Erro na análise: {str(e)}",
                confidence=0.0
            )

class TaskExecutorAgent(BaseAgent):
    """Agente executor que realiza tarefas específicas baseadas em documentos"""
    
    def __init__(self, rag_system=None):
        config = AgentConfig(
            name="Task Executor Agent",
            description="Agente que executa tarefas específicas baseadas em conhecimento dos documentos",
            system_prompt="""Você é um agente executor que realiza tarefas específicas baseadas 
            no conhecimento extraído dos documentos. Use o sistema RAG para obter informações 
            necessárias e execute as tarefas de forma eficiente e precisa.""",
            tools=["rag_query", "search_documents"],
            memory=True,
            temperature=0.5,
            max_iterations=10
        )
        super().__init__(config, rag_system)
    
    def execute_task(self, task_description: str) -> AgentResponse:
        """
        Executa uma tarefa específica
        
        Args:
            task_description: Descrição da tarefa
            
        Returns:
            Resultado da execução
        """
        try:
            # Criar prompt de execução
            execution_prompt = f"""
            Execute a seguinte tarefa usando as informações disponíveis nos documentos:
            
            TAREFA: {task_description}
            
            Por favor:
            1. Identifique as informações necessárias nos documentos
            2. Execute a tarefa passo a passo
            3. Forneça um relatório detalhado da execução
            4. Inclua quaisquer recomendações ou observações
            """
            
            # Executar tarefa
            response = self.process(execution_prompt)
            
            # Adicionar metadados da execução
            response.metadata.update({
                "task": task_description,
                "execution_time": datetime.now().isoformat(),
                "task_type": "document_based_execution"
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na execução da tarefa: {str(e)}")
            return AgentResponse(
                content=f"Erro na execução: {str(e)}",
                confidence=0.0
            )

class MultiAgentSystem:
    """Sistema que coordena múltiplos agentes"""
    
    def __init__(self, rag_system=None):
        """
        Inicializa o sistema multi-agente
        
        Args:
            rag_system: Sistema RAG para consulta
        """
        self.rag_system = rag_system
        self.agents = {}
        self.coordinator_llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.5,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Inicializar agentes padrão
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Inicializa os agentes padrão"""
        self.agents["conversational"] = ConversationalAgent(self.rag_system)
        self.agents["research"] = ResearchAgent(self.rag_system)
        self.agents["executor"] = TaskExecutorAgent(self.rag_system)
    
    def add_agent(self, name: str, agent: BaseAgent):
        """Adiciona um novo agente ao sistema"""
        self.agents[name] = agent
    
    def route_request(self, user_input: str) -> str:
        """
        Roteia a requisição para o agente mais apropriado
        
        Args:
            user_input: Entrada do usuário
            
        Returns:
            Nome do agente recomendado
        """
        routing_prompt = f"""
        Analise a seguinte entrada do usuário e determine qual agente é mais apropriado:
        
        Entrada: {user_input}
        
        Agentes disponíveis:
        - conversational: Para conversas gerais e perguntas
        - research: Para análise e pesquisa de documentos
        - executor: Para execução de tarefas específicas
        
        Responda apenas com o nome do agente mais apropriado.
        """
        
        try:
            response = self.coordinator_llm.predict(routing_prompt)
            agent_name = response.strip().lower()
            
            if agent_name in self.agents:
                return agent_name
            else:
                return "conversational"  # Fallback
                
        except Exception as e:
            logger.error(f"Erro no roteamento: {str(e)}")
            return "conversational"
    
    def process_with_coordination(self, user_input: str) -> AgentResponse:
        """
        Processa a entrada com coordenação entre agentes
        
        Args:
            user_input: Entrada do usuário
            
        Returns:
            Resposta coordenada
        """
        try:
            # Rotear para o agente apropriado
            agent_name = self.route_request(user_input)
            agent = self.agents[agent_name]
            
            # Processar com o agente selecionado
            response = agent.process(user_input)
            
            # Adicionar metadados de coordenação
            response.metadata.update({
                "coordinated_by": "multi_agent_system",
                "selected_agent": agent_name,
                "available_agents": list(self.agents.keys())
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no processamento coordenado: {str(e)}")
            return AgentResponse(
                content=f"Erro no processamento: {str(e)}",
                confidence=0.0
            )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Obtém o status de todos os agentes"""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "name": agent.config.name,
                "description": agent.config.description,
                "tools": agent.config.tools,
                "memory_enabled": agent.config.memory,
                "model": agent.config.model_name,
                "temperature": agent.config.temperature
            }
        return status

# Função de conveniência para criar agentes
def create_agent(agent_type: str, rag_system=None) -> BaseAgent:
    """
    Cria um agente do tipo especificado
    
    Args:
        agent_type: Tipo do agente (conversational, research, executor)
        rag_system: Sistema RAG para consulta
        
    Returns:
        Instância do agente
    """
    agent_map = {
        "conversational": ConversationalAgent,
        "research": ResearchAgent,
        "executor": TaskExecutorAgent
    }
    
    if agent_type not in agent_map:
        raise ValueError(f"Tipo de agente não suportado: {agent_type}")
    
    return agent_map[agent_type](rag_system) 