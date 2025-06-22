"""
Sistema de Agentes de IA integrado com RAG
Implementa diferentes tipos de agentes com capacidades específicas
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from rag_system import RAGSystem
from llm_providers import llm_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definição de uma classe de configuração simples para manter a compatibilidade
class AgentConfig:
    def __init__(self, agent_id=None, agent_name=None, model_name="gpt-3.5-turbo", temperature=0.7, system_prompt="Você é um assistente prestativo.", memory=True, max_iterations=5, tools=None, provider="openai"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.memory = memory
        self.max_iterations = max_iterations
        self.tools = tools if tools is not None else ["rag_query", "search_documents"]
        self.provider = provider

class MultiLLMAgent:
    """Agente que pode usar múltiplos LLMs simultaneamente para comparação"""
    
    def __init__(self, config: AgentConfig, rag_system=None, providers: List[str] = None):
        """
        Inicializa o agente multi-LLM
        
        Args:
            config: Configuração do agente
            rag_system: Sistema RAG para consulta
            providers: Lista de provedores a usar (ex: ['openai', 'openrouter', 'gemini'])
        """
        self.config = config
        self.rag_system = rag_system
        self.providers = providers or ['openai']  # Padrão: apenas OpenAI
        
        # Verificar provedores disponíveis
        available_providers = llm_manager.list_available_providers()
        self.providers = [p for p in self.providers if p in available_providers]
        
        if not self.providers:
            if available_providers:
                self.providers = [available_providers[0]]
                logger.warning(f"Nenhum provedor solicitado disponível. Usando: {self.providers[0]}")
            else:
                raise ValueError("Nenhum provedor de IA configurado")
        
        # Criar agentes para cada provedor
        self.agents = {}
        for provider in self.providers:
            try:
                agent_config = AgentConfig(
                    agent_id=config.agent_id,
                    agent_name=f"{config.agent_name} ({provider})",
                    model_name=config.model_name,
                    temperature=config.temperature,
                    system_prompt=config.system_prompt,
                    memory=config.memory,
                    max_iterations=config.max_iterations,
                    tools=config.tools,
                    provider=provider
                )
                self.agents[provider] = BaseAgent(agent_config, rag_system)
            except Exception as e:
                logger.error(f"Erro ao criar agente para {provider}: {e}")
        
        # Memória compartilhada entre todos os agentes
        self.shared_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        ) if config.memory else None
        
        logger.info(f"Agente multi-LLM criado com provedores: {list(self.agents.keys())}")
    
    def process_message_multi_llm(self, message: str) -> Dict[str, Any]:
        """
        Processa uma mensagem com múltiplos LLMs e retorna todas as respostas
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Dict com respostas de todos os LLMs
        """
        results = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'responses': {},
            'errors': {},
            'comparison': {}
        }
        
        # Processar com cada LLM
        for provider, agent in self.agents.items():
            try:
                # Usar memória compartilhada se disponível
                if self.shared_memory:
                    # Adicionar mensagem do usuário à memória compartilhada
                    self.shared_memory.chat_memory.add_user_message(message)
                    
                    # Criar mensagens com histórico
                    messages = []
                    chat_history = self.shared_memory.chat_memory.messages
                    
                    # Adicionar prompt do sistema
                    if self.config.system_prompt:
                        messages.append({
                            "role": "system",
                            "content": self.config.system_prompt
                        })
                    
                    # Adicionar histórico (últimas 4 mensagens)
                    for msg in chat_history[-4:]:
                        if isinstance(msg, HumanMessage):
                            messages.append({"role": "user", "content": msg.content})
                        elif isinstance(msg, AIMessage):
                            messages.append({"role": "assistant", "content": msg.content})
                    
                    # Gerar resposta usando o provedor específico
                    llm_manager.set_active_provider(provider)
                    response = llm_manager.generate_response(
                        messages,
                        model=agent.config.model_name,
                        temperature=agent.config.temperature
                    )
                    
                    # Adicionar resposta à memória compartilhada
                    self.shared_memory.chat_memory.add_ai_message(response)
                else:
                    # Sem memória, usar o agente diretamente
                    response = agent.process_message(message)
                
                results['responses'][provider] = {
                    'response': response,
                    'model': agent.config.model_name,
                    'temperature': agent.config.temperature,
                    'provider': provider
                }
                
            except Exception as e:
                logger.error(f"Erro ao processar com {provider}: {e}")
                results['errors'][provider] = str(e)
        
        # Adicionar informações de comparação
        if len(results['responses']) > 1:
            results['comparison'] = self._compare_responses(results['responses'])
        
        return results
    
    def _compare_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Compara as respostas dos diferentes LLMs"""
        comparison = {
            'response_lengths': {},
            'response_times': {},
            'unique_responses': len(set(r['response'] for r in responses.values())),
            'providers_used': list(responses.keys())
        }
        
        for provider, data in responses.items():
            comparison['response_lengths'][provider] = len(data['response'])
        
        return comparison
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o agente multi-LLM"""
        return {
            "agent_id": self.config.agent_id,
            "agent_name": self.config.agent_name,
            "providers": list(self.agents.keys()),
            "models": {p: a.config.model_name for p, a in self.agents.items()},
            "temperature": self.config.temperature,
            "system_prompt": self.config.system_prompt,
            "memory_enabled": self.config.memory
        }
    
    def add_provider(self, provider: str) -> bool:
        """Adiciona um novo provedor ao agente"""
        try:
            if provider not in llm_manager.list_available_providers():
                logger.error(f"Provedor {provider} não disponível")
                return False
            
            if provider in self.agents:
                logger.warning(f"Provedor {provider} já está sendo usado")
                return True
            
            # Criar novo agente para o provedor
            agent_config = AgentConfig(
                agent_id=self.config.agent_id,
                agent_name=f"{self.config.agent_name} ({provider})",
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                system_prompt=self.config.system_prompt,
                memory=self.config.memory,
                max_iterations=self.config.max_iterations,
                tools=self.config.tools,
                provider=provider
            )
            
            self.agents[provider] = BaseAgent(agent_config, self.rag_system)
            logger.info(f"Provedor {provider} adicionado ao agente")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar provedor {provider}: {e}")
            return False
    
    def remove_provider(self, provider: str) -> bool:
        """Remove um provedor do agente"""
        if provider in self.agents:
            del self.agents[provider]
            logger.info(f"Provedor {provider} removido do agente")
            return True
        return False
    
    def reset_memory(self):
        """Reseta a memória compartilhada"""
        if self.shared_memory:
            self.shared_memory.clear()

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
        
        # Configurar provedor de IA
        if config.provider not in llm_manager.list_available_providers():
            available = llm_manager.list_available_providers()
            if not available:
                raise ValueError("Nenhum provedor de IA configurado")
            else:
                logger.warning(f"Provedor '{config.provider}' não disponível. Usando '{available[0]}'")
                config.provider = available[0]
        
        # Definir provedor ativo
        llm_manager.set_active_provider(config.provider)

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

    def _rag_query_tool(self, query: str) -> str:
        """Ferramenta para consultar o sistema RAG"""
        try:
            if not self.rag_system:
                return "Sistema RAG não disponível"
            
            result = self.rag_system.query(query)
            return result["answer"]
        except Exception as e:
            logger.error(f"Erro na consulta RAG: {e}")
            return f"Erro ao consultar documentos: {str(e)}"

    def _search_documents_tool(self, query: str) -> str:
        """Ferramenta para buscar documentos similares"""
        try:
            if not self.rag_system:
                return "Sistema RAG não disponível"
            
            results = self.rag_system.search_similar_documents(query, k=3)
            if not results:
                return "Nenhum documento similar encontrado"
            
            response = "Documentos similares encontrados:\n\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. {result['content'][:200]}...\n"
                if 'source' in result['metadata']:
                    response += f"   Fonte: {result['metadata']['source']}\n\n"
            
            return response
        except Exception as e:
            logger.error(f"Erro na busca de documentos: {e}")
            return f"Erro ao buscar documentos: {str(e)}"

    def _create_agent(self):
        """Cria o agente LangChain"""
        try:
            # Usar o gerenciador de provedores para gerar respostas
            def llm_generate(messages: List[Dict[str, str]]) -> str:
                return llm_manager.generate_response(
                    messages,
                    model=self.config.model_name,
                    temperature=self.config.temperature
                )
            
            # Criar agente customizado
            class CustomAgent:
                def __init__(self, config, tools, memory):
                    self.config = config
                    self.tools = tools
                    self.memory = memory
                
                def run(self, input_text: str) -> str:
                    # Construir mensagens
                    messages = []
                    
                    # Adicionar prompt do sistema
                    if self.config.system_prompt:
                        messages.append({
                            "role": "system",
                            "content": self.config.system_prompt
                        })
                    
                    # Adicionar histórico se disponível
                    if self.memory:
                        chat_history = self.memory.chat_memory.messages
                        for msg in chat_history[-4:]:  # Últimas 4 mensagens
                            if isinstance(msg, HumanMessage):
                                messages.append({"role": "user", "content": msg.content})
                            elif isinstance(msg, AIMessage):
                                messages.append({"role": "assistant", "content": msg.content})
                    
                    # Adicionar mensagem atual
                    messages.append({"role": "user", "content": input_text})
                    
                    # Gerar resposta
                    response = llm_generate(messages)
                    
                    # Atualizar memória
                    if self.memory:
                        self.memory.chat_memory.add_user_message(input_text)
                        self.memory.chat_memory.add_ai_message(response)
                    
                    return response
            
            return CustomAgent(self.config, self.tools, self.memory)
            
        except Exception as e:
            logger.error(f"Erro ao criar agente: {e}")
            raise

    def process_message(self, message: str) -> str:
        """
        Processa uma mensagem do usuário
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Resposta do agente
        """
        try:
            # Registrar ação
            self.action_history.append({
                "timestamp": datetime.now(),
                "action": "process_message",
                "input": message
            })
            
            # Processar com o agente
            response = self.agent.run(message)
            
            # Registrar resposta
            self.action_history.append({
                "timestamp": datetime.now(),
                "action": "generate_response",
                "output": response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"

    def get_agent_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o agente"""
        return {
            "agent_id": self.config.agent_id,
            "agent_name": self.config.agent_name,
            "model_name": self.config.model_name,
            "temperature": self.config.temperature,
            "system_prompt": self.config.system_prompt,
            "provider": self.config.provider,
            "tools": self.config.tools,
            "memory_enabled": self.config.memory,
            "action_count": len(self.action_history)
        }

    def reset_memory(self):
        """Reseta a memória do agente"""
        if self.memory:
            self.memory.clear()
        self.action_history = []

class ConversationalAgent(BaseAgent):
    """Agente especializado em conversas naturais"""
    
    def __init__(self, rag_system=None):
        config = AgentConfig(
            agent_name="Agente Conversacional",
            model_name="gpt-3.5-turbo",
            temperature=0.8,
            system_prompt="""Você é um assistente conversacional amigável e prestativo. 
            Sua função é manter conversas naturais e úteis com os usuários.
            Seja cordial, empático e sempre tente ajudar da melhor forma possível.""",
            memory=True,
            tools=["rag_query"],
            provider="openai"
        )
        super().__init__(config, rag_system)

class ResearchAgent(BaseAgent):
    """Agente especializado em pesquisa e análise"""
    
    def __init__(self, rag_system=None):
        config = AgentConfig(
            agent_name="Agente de Pesquisa",
            model_name="gpt-4o-mini",
            temperature=0.3,
            system_prompt="""Você é um agente de pesquisa especializado em análise profunda e busca de informações.
            Sua função é:
            1. Analisar documentos e fontes de informação
            2. Extrair insights relevantes
            3. Fornecer análises detalhadas e bem fundamentadas
            4. Identificar padrões e conexões entre informações
            5. Apresentar conclusões baseadas em evidências""",
            memory=True,
            tools=["rag_query", "search_documents"],
            provider="openai"
        )
        super().__init__(config, rag_system)

class TaskExecutorAgent(BaseAgent):
    """Agente especializado em execução de tarefas específicas"""
    
    def __init__(self, rag_system=None):
        config = AgentConfig(
            agent_name="Agente Executor",
            model_name="gpt-3.5-turbo",
            temperature=0.2,
            system_prompt="""Você é um agente executor especializado em realizar tarefas específicas de forma eficiente.
            Sua função é:
            1. Identificar a tarefa solicitada
            2. Planejar os passos necessários
            3. Executar cada passo de forma sistemática
            4. Fornecer resultados claros e acionáveis
            5. Documentar o processo realizado""",
            memory=True,
            tools=["rag_query", "search_documents"],
            provider="openai"
        )
        super().__init__(config, rag_system)

def create_agent(agent_type: str, rag_system=None, **kwargs) -> BaseAgent:
    """
    Factory function para criar agentes
    
    Args:
        agent_type: Tipo do agente (conversational, research, executor, custom, multi_llm)
        rag_system: Sistema RAG opcional
        **kwargs: Configurações adicionais
        
    Returns:
        Instância do agente criado
    """
    if agent_type == "conversational":
        return ConversationalAgent(rag_system)
    elif agent_type == "research":
        return ResearchAgent(rag_system)
    elif agent_type == "executor":
        return TaskExecutorAgent(rag_system)
    elif agent_type == "multi_llm":
        # Criar agente multi-LLM
        providers = kwargs.get("providers", ["openai"])
        config = AgentConfig(
            agent_name=kwargs.get("name", "Agente Multi-LLM"),
            model_name=kwargs.get("model_name", "gpt-3.5-turbo"),
            temperature=kwargs.get("temperature", 0.7),
            system_prompt=kwargs.get("system_prompt", "Você é um assistente prestativo."),
            memory=kwargs.get("memory", True),
            tools=kwargs.get("tools", ["rag_query"]),
            provider="multi"
        )
        return MultiLLMAgent(config, rag_system, providers)
    elif agent_type == "custom":
        # Criar agente customizado com configurações específicas
        config = AgentConfig(
            agent_name=kwargs.get("name", "Agente Customizado"),
            model_name=kwargs.get("model_name", "gpt-3.5-turbo"),
            temperature=kwargs.get("temperature", 0.7),
            system_prompt=kwargs.get("system_prompt", "Você é um assistente prestativo."),
            memory=kwargs.get("memory", True),
            tools=kwargs.get("tools", ["rag_query"]),
            provider=kwargs.get("provider", "openai")
        )
        return BaseAgent(config, rag_system)
    else:
        raise ValueError(f"Tipo de agente desconhecido: {agent_type}")

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
        
        # Configurar provedor para o coordenador
        available_providers = llm_manager.list_available_providers()
        if available_providers:
            llm_manager.set_active_provider(available_providers[0])
        
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
        logger.info(f"Agente '{name}' adicionado ao sistema")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Obtém um agente específico"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """Lista todos os agentes disponíveis"""
        return list(self.agents.keys())
    
    def process_with_agent(self, agent_name: str, message: str) -> str:
        """
        Processa uma mensagem com um agente específico
        
        Args:
            agent_name: Nome do agente
            message: Mensagem a ser processada
            
        Returns:
            Resposta do agente
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return f"Agente '{agent_name}' não encontrado"
        
        return agent.process_message(message)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o sistema multi-agente"""
        return {
            "total_agents": len(self.agents),
            "available_agents": self.list_agents(),
            "agents_info": {
                name: agent.get_agent_info() 
                for name, agent in self.agents.items()
            }
        } 