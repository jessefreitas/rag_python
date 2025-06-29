"""
Configuração e gerenciamento de modelos LLM
Sistema RAG Python v1.5.3
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import json

@dataclass
class ModelInfo:
    """Informações de um modelo LLM"""
    name: str
    provider: str
    description: str
    context_length: int
    supports_vision: bool = False
    supports_function_calling: bool = False
    cost_per_1k_tokens: float = 0.0
    emoji: str = "🤖"

class ModelsManager:
    """Gerenciador de modelos LLM"""
    
    def __init__(self):
        self.models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Inicializa catálogo de modelos"""
        return {
            # OpenAI Models
            "gpt-4o": ModelInfo(
                name="gpt-4o",
                provider="openai",
                description="🚀 GPT-4o - Modelo mais avançado da OpenAI",
                context_length=128000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.005,
                emoji="🚀"
            ),
            "gpt-4o-mini": ModelInfo(
                name="gpt-4o-mini",
                provider="openai",
                description="⚡ GPT-4o Mini - Rápido e eficiente",
                context_length=128000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.00015,
                emoji="⚡"
            ),
            "gpt-4-turbo": ModelInfo(
                name="gpt-4-turbo",
                provider="openai",
                description="🏎️ GPT-4 Turbo - Alta performance",
                context_length=128000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.01,
                emoji="🏎️"
            ),
            "gpt-4": ModelInfo(
                name="gpt-4",
                provider="openai",
                description="🧠 GPT-4 - Modelo clássico avançado",
                context_length=8192,
                supports_function_calling=True,
                cost_per_1k_tokens=0.03,
                emoji="🧠"
            ),
            "gpt-3.5-turbo": ModelInfo(
                name="gpt-3.5-turbo",
                provider="openai",
                description="💨 GPT-3.5 Turbo - Rápido e confiável",
                context_length=16385,
                supports_function_calling=True,
                cost_per_1k_tokens=0.001,
                emoji="💨"
            ),
            
            # Google Models
            "gemini-1.5-pro": ModelInfo(
                name="gemini-1.5-pro",
                provider="google",
                description="💎 Gemini 1.5 Pro - Modelo premium do Google",
                context_length=2000000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.00125,
                emoji="💎"
            ),
            "gemini-1.5-flash": ModelInfo(
                name="gemini-1.5-flash",
                provider="google",
                description="⚡ Gemini 1.5 Flash - Velocidade otimizada",
                context_length=1000000,
                supports_vision=True,
                supports_function_calling=True,
                cost_per_1k_tokens=0.00035,
                emoji="⚡"
            ),
            "gemini-pro": ModelInfo(
                name="gemini-pro",
                provider="google",
                description="🌟 Gemini Pro - Modelo principal do Google",
                context_length=32768,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0005,
                emoji="🌟"
            ),
            "gemini-pro-vision": ModelInfo(
                name="gemini-pro-vision",
                provider="google",
                description="👁️ Gemini Pro Vision - Análise de imagens",
                context_length=16384,
                supports_vision=True,
                cost_per_1k_tokens=0.00025,
                emoji="👁️"
            ),
            
            # OpenRouter Models
            "anthropic/claude-3.5-sonnet": ModelInfo(
                name="anthropic/claude-3.5-sonnet",
                provider="openrouter",
                description="🎼 Claude 3.5 Sonnet - Excelente para escrita",
                context_length=200000,
                supports_function_calling=True,
                cost_per_1k_tokens=0.003,
                emoji="🎼"
            ),
            "anthropic/claude-3-haiku": ModelInfo(
                name="anthropic/claude-3-haiku",
                provider="openrouter",
                description="🌸 Claude 3 Haiku - Rápido e conciso",
                context_length=200000,
                cost_per_1k_tokens=0.00025,
                emoji="🌸"
            ),
            "meta-llama/llama-3.1-405b-instruct": ModelInfo(
                name="meta-llama/llama-3.1-405b-instruct",
                provider="openrouter",
                description="🦙 Llama 3.1 405B - Modelo gigante da Meta",
                context_length=131072,
                supports_function_calling=True,
                cost_per_1k_tokens=0.005,
                emoji="🦙"
            ),
            "mistralai/mistral-large": ModelInfo(
                name="mistralai/mistral-large",
                provider="openrouter",
                description="🌪️ Mistral Large - Modelo europeu avançado",
                context_length=128000,
                supports_function_calling=True,
                cost_per_1k_tokens=0.008,
                emoji="🌪️"
            ),
            "google/gemma-2-27b-it": ModelInfo(
                name="google/gemma-2-27b-it",
                provider="openrouter",
                description="💫 Gemma 2 27B - Modelo open source do Google",
                context_length=8192,
                cost_per_1k_tokens=0.0001,
                emoji="💫"
            ),
            
            # DeepSeek Models
            "deepseek-chat": ModelInfo(
                name="deepseek-chat",
                provider="deepseek",
                description="🔮 DeepSeek Chat - Conversação avançada",
                context_length=32768,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0001,
                emoji="🔮"
            ),
            "deepseek-coder": ModelInfo(
                name="deepseek-coder",
                provider="deepseek",
                description="💻 DeepSeek Coder - Especialista em programação",
                context_length=16384,
                supports_function_calling=True,
                cost_per_1k_tokens=0.0001,
                emoji="💻"
            ),
            "deepseek-math": ModelInfo(
                name="deepseek-math",
                provider="deepseek",
                description="🧮 DeepSeek Math - Especialista em matemática",
                context_length=4096,
                cost_per_1k_tokens=0.0001,
                emoji="🧮"
            )
        }
    
    def get_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """Retorna modelos de um provedor específico"""
        return [model for model in self.models.values() if model.provider == provider]
    
    def get_model_info(self, model_name: str) -> ModelInfo:
        """Retorna informações de um modelo específico"""
        return self.models.get(model_name)
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        providers = set(model.provider for model in self.models.values())
        return sorted(list(providers))
    
    def get_models_with_vision(self) -> List[ModelInfo]:
        """Retorna modelos que suportam visão"""
        return [model for model in self.models.values() if model.supports_vision]
    
    def get_models_with_functions(self) -> List[ModelInfo]:
        """Retorna modelos que suportam function calling"""
        return [model for model in self.models.values() if model.supports_function_calling]
    
    def get_cheapest_models(self, limit: int = 5) -> List[ModelInfo]:
        """Retorna os modelos mais baratos"""
        sorted_models = sorted(self.models.values(), key=lambda x: x.cost_per_1k_tokens)
        return sorted_models[:limit]
    
    def search_models(self, query: str) -> List[ModelInfo]:
        """Busca modelos por nome ou descrição"""
        query = query.lower()
        results = []
        for model in self.models.values():
            if (query in model.name.lower() or 
                query in model.description.lower() or 
                query in model.provider.lower()):
                results.append(model)
        return results
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estatísticas por provedor"""
        stats = {}
        for provider in self.get_available_providers():
            provider_models = self.get_models_by_provider(provider)
            stats[provider] = {
                'total_models': len(provider_models),
                'vision_models': len([m for m in provider_models if m.supports_vision]),
                'function_models': len([m for m in provider_models if m.supports_function_calling]),
                'avg_cost': sum(m.cost_per_1k_tokens for m in provider_models) / len(provider_models),
                'max_context': max(m.context_length for m in provider_models),
                'models': [m.name for m in provider_models]
            }
        return stats
    
    def get_provider_models_simple(self) -> Dict[str, List[str]]:
        """Retorna dicionário simples de modelos por provedor"""
        result = {}
        for provider in self.get_available_providers():
            result[provider] = [model.name for model in self.get_models_by_provider(provider)]
        return result
    
    def export_catalog(self) -> Dict[str, Any]:
        """Exporta catálogo completo para JSON"""
        catalog = {
            'version': '1.5.3',
            'total_models': len(self.models),
            'providers': self.get_available_providers(),
            'models': {}
        }
        
        for name, model in self.models.items():
            catalog['models'][name] = {
                'name': model.name,
                'provider': model.provider,
                'description': model.description,
                'context_length': model.context_length,
                'supports_vision': model.supports_vision,
                'supports_function_calling': model.supports_function_calling,
                'cost_per_1k_tokens': model.cost_per_1k_tokens,
                'emoji': model.emoji
            }
        
        return catalog
    
    def get_provider_models_simple(self) -> Dict[str, List[str]]:
        """Retorna dicionário simples de modelos por provedor"""
        result = {}
        for provider in self.get_available_providers():
            result[provider] = [model.name for model in self.get_models_by_provider(provider)]
        return result

# Instância global do gerenciador
models_manager = ModelsManager()

def get_safe_models() -> List[str]:
    """Retorna lista de modelos seguros para usar"""
    return [
        "gpt-4o-mini",
        "gpt-3.5-turbo", 
        "gemini-1.5-flash",
        "deepseek-chat"
    ]

def get_provider_models(provider: str) -> List[str]:
    """Retorna nomes dos modelos de um provedor"""
    return [model.name for model in models_manager.get_models_by_provider(provider)]

def get_provider_models_simple() -> Dict[str, List[str]]:
    """Retorna dicionário simples de modelos por provedor"""
    result = {}
    for provider in models_manager.get_available_providers():
        result[provider] = [model.name for model in models_manager.get_models_by_provider(provider)]
    return result

def get_model_display_name(model_name: str) -> str:
    """Retorna nome formatado para exibição"""
    model_info = models_manager.get_model_info(model_name)
    if model_info:
        return f"{model_info.emoji} {model_info.name}"
    return model_name

def validate_model_availability(model_name: str, provider: str) -> bool:
    """Valida se modelo está disponível para o provedor"""
    model_info = models_manager.get_model_info(model_name)
    return model_info is not None and model_info.provider == provider

# Configurações de compatibilidade
PROVIDER_MODEL_MAP = {
    'openai': [
        'gpt-4o',
        'gpt-4o-mini', 
        'gpt-4-turbo',
        'gpt-4',
        'gpt-3.5-turbo'
    ],
    'google': [
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-pro',
        'gemini-pro-vision'
    ],
    'openrouter': [
        'anthropic/claude-3.5-sonnet',
        'anthropic/claude-3-haiku',
        'meta-llama/llama-3.1-405b-instruct',
        'mistralai/mistral-large',
        'google/gemma-2-27b-it'
    ],
    'deepseek': [
        'deepseek-chat',
        'deepseek-coder',
        'deepseek-math'
    ]
}

if __name__ == "__main__":
    # Teste do sistema
    print("🤖 RAG Python - Catálogo de Modelos LLM v1.5.3")
    print("=" * 50)
    
    stats = models_manager.get_provider_stats()
    for provider, data in stats.items():
        print(f"\n📊 {provider.upper()}:")
        print(f"  - Modelos: {data['total_models']}")
        print(f"  - Com visão: {data['vision_models']}")
        print(f"  - Com funções: {data['function_models']}")
        print(f"  - Custo médio: ${data['avg_cost']:.6f}/1k tokens")
        print(f"  - Contexto máximo: {data['max_context']:,} tokens")
    
    print(f"\n✅ Total: {len(models_manager.models)} modelos carregados")
    print("🚀 Sistema pronto para uso!") 