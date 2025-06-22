"""
Módulo para gerenciar múltiplos provedores de IA
Suporta OpenRouter, OpenAI e Google Gemini
"""

import os
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass

from openai import OpenAI
import google.generativeai as genai
import requests

logger = logging.getLogger(__name__)

@dataclass
class ProviderConfig:
    """Configuração para um provedor de IA"""
    name: str
    api_key: str
    base_url: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000

class BaseLLMProvider(ABC):
    """Classe base abstrata para provedores de IA"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Gera uma resposta baseada nas mensagens fornecidas"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """Lista os modelos disponíveis para este provedor"""
        pass

class OpenRouterProvider(BaseLLMProvider):
    """Provedor OpenRouter - Acesso unificado a múltiplos modelos"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.api_key
        )
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Gera resposta usando OpenRouter"""
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', self.config.model_name),
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                extra_headers={
                    "HTTP-Referer": kwargs.get('site_url', 'http://localhost:3000'),
                    "X-Title": kwargs.get('site_name', 'RAG Python System'),
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta via OpenRouter: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis no OpenRouter"""
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {self.config.api_key}"}
            )
            if response.status_code == 200:
                models = response.json()
                return [model['id'] for model in models.get('data', [])]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar modelos OpenRouter: {e}")
            return []

class OpenAIProvider(BaseLLMProvider):
    """Provedor OpenAI - Acesso direto aos modelos OpenAI"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Gera resposta usando OpenAI"""
        try:
            # Garante que o modelo não seja vazio ou None
            model = kwargs.get('model', self.config.model_name)
            if not model or not model.strip():
                model = self.config.model_name
                
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta via OpenAI: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis na OpenAI"""
        try:
            response = self.client.models.list()
            return [model.id for model in response.data if 'gpt' in model.id]
        except Exception as e:
            logger.error(f"Erro ao listar modelos OpenAI: {e}")
            return []

class GoogleGeminiProvider(BaseLLMProvider):
    """Provedor Google Gemini"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model_name)
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Gera resposta usando Google Gemini"""
        try:
            # Converter formato de mensagens para Gemini
            prompt = self._convert_messages_to_prompt(messages)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', self.config.temperature),
                    max_output_tokens=kwargs.get('max_tokens', self.config.max_tokens)
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta via Google Gemini: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Converte mensagens do formato OpenAI para prompt do Gemini"""
        prompt = ""
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt += f"System: {content}\n\n"
            elif role == 'user':
                prompt += f"User: {content}\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n"
        
        return prompt
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis no Google Gemini"""
        try:
            models = genai.list_models()
            return [model.name for model in models if 'gemini' in model.name.lower()]
        except Exception as e:
            logger.error(f"Erro ao listar modelos Google Gemini: {e}")
            return []

class LLMProviderManager:
    """Gerenciador central para todos os provedores de IA"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.active_provider: Optional[str] = None
        self._load_providers()
    
    def _load_providers(self):
        """Carrega provedores baseado nas variáveis de ambiente"""
        
        # OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            config = ProviderConfig(
                name="openrouter",
                api_key=openrouter_key,
                model_name="openai/gpt-4o-mini"
            )
            self.providers["openrouter"] = OpenRouterProvider(config)
            if not self.active_provider:
                self.active_provider = "openrouter"
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            config = ProviderConfig(
                name="openai",
                api_key=openai_key,
                model_name="gpt-3.5-turbo"
            )
            self.providers["openai"] = OpenAIProvider(config)
            if not self.active_provider:
                self.active_provider = "openai"
        
        # Google Gemini
        gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if gemini_key:
            config = ProviderConfig(
                name="gemini",
                api_key=gemini_key,
                model_name="gemini-1.5-flash"
            )
            self.providers["gemini"] = GoogleGeminiProvider(config)
            if not self.active_provider:
                self.active_provider = "gemini"
    
    def set_active_provider(self, provider_name: str) -> bool:
        """Define o provedor ativo"""
        if provider_name in self.providers:
            self.active_provider = provider_name
            return True
        return False
    
    def get_active_provider(self) -> Optional[BaseLLMProvider]:
        """Retorna o provedor ativo"""
        if self.active_provider:
            return self.providers[self.active_provider]
        return None
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Gera resposta usando o provedor ativo"""
        provider = self.get_active_provider()
        if not provider:
            raise ValueError("Nenhum provedor de IA configurado")
        
        return provider.generate_response(messages, **kwargs)
    
    def list_available_providers(self) -> List[str]:
        """Lista provedores disponíveis"""
        return list(self.providers.keys())
    
    def get_provider_models(self, provider_name: str) -> List[str]:
        """Lista modelos disponíveis para um provedor específico"""
        if provider_name in self.providers:
            return self.providers[provider_name].list_models()
        return []
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações sobre os provedores configurados"""
        info = {
            "active_provider": self.active_provider,
            "available_providers": self.list_available_providers(),
            "providers": {}
        }
        
        for name, provider in self.providers.items():
            info["providers"][name] = {
                "name": provider.config.name,
                "model_name": provider.config.model_name,
                "temperature": provider.config.temperature,
                "max_tokens": provider.config.max_tokens
            }
        
        return info

# Instância global do gerenciador
llm_manager = LLMProviderManager() 