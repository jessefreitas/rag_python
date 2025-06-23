#!/usr/bin/env python3
"""
🔧 CORREÇÃO DO ROTEAMENTO DE PROVEDORES LLM
Corrige o problema onde modelos de diferentes provedores são enviados para OpenAI
"""

import os
import re

def fix_llm_routing():
    """Corrige o roteamento de provedores no arquivo llm_providers.py"""
    
    # Ler arquivo original
    with open('llm_providers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fazer backup
    with open('llm_providers.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Aplicar correções específicas
    corrections = [
        # Corrigir variável de ambiente do Google
        ('GOOGLE_GEMINI_API_KEY', 'GOOGLE_API_KEY'),
        
        # Corrigir nome do provedor Google no dicionário
        ('self.providers["gemini"]', 'self.providers["google"]'),
        ('self.active_provider = "gemini"', 'self.active_provider = "google"'),
        
        # Corrigir nome do provedor na configuração
        ('name="gemini"', 'name="google"'),
    ]
    
    for old, new in corrections:
        content = content.replace(old, new)
    
    # Adicionar validação de modelo por provedor
    validation_code = '''
    def _validate_model_for_provider(self, provider_name: str, model: str) -> str:
        """Valida se o modelo é compatível com o provedor"""
        
        # Mapeamento de modelos por provedor
        provider_models = {
            'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'],
            'google': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro', 'gemini-pro-vision'],
            'openrouter': ['openai/gpt-4o', 'openai/gpt-4o-mini', 'anthropic/claude-3.5-sonnet', 
                          'anthropic/claude-3-haiku', 'meta-llama/llama-3.1-405b-instruct'],
            'deepseek': ['deepseek-chat', 'deepseek-coder', 'deepseek-math']
        }
        
        # Se o provedor não tem modelos mapeados, usar modelo padrão
        if provider_name not in provider_models:
            return self.providers[provider_name].config.model_name
        
        # Se o modelo não é compatível com o provedor, usar modelo padrão
        valid_models = provider_models[provider_name]
        if model not in valid_models:
            return self.providers[provider_name].config.model_name
        
        return model
'''
    
    # Inserir a função de validação antes da função generate_response
    pattern = r'(def generate_response\(self, messages: List\[Dict\[str, str\]\], provider_name: str = None, \*\*kwargs\) -> Dict\[str, Any\]:)'
    content = re.sub(pattern, validation_code + '\n    \\1', content)
    
    # Modificar a função generate_response para usar validação
    old_generate = '''            # Gerar resposta
            response = provider.generate_response(messages, **kwargs)'''
    
    new_generate = '''            # Validar modelo para o provedor
            model = kwargs.get('model')
            if model:
                validated_model = self._validate_model_for_provider(provider_name or self.active_provider, model)
                kwargs['model'] = validated_model
            
            # Gerar resposta
            response = provider.generate_response(messages, **kwargs)'''
    
    content = content.replace(old_generate, new_generate)
    
    # Salvar arquivo corrigido
    with open('llm_providers.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Correções aplicadas em llm_providers.py")
    print("📄 Backup salvo como llm_providers.py.backup")

def create_provider_test():
    """Cria um script de teste para os provedores"""
    
    test_code = '''#!/usr/bin/env python3
"""
🧪 TESTE DOS PROVEDORES LLM CORRIGIDOS
"""

import os
import sys
from llm_providers import LLMProviderManager

def test_providers():
    """Testa os provedores com modelos corretos"""
    
    manager = LLMProviderManager()
    
    # Testes por provedor
    tests = [
        # OpenAI (deve funcionar)
        ("openai", "gpt-3.5-turbo", "Olá, como você está funcionando?"),
        ("openai", "gpt-4o-mini", "Teste modelo gpt-4o-mini"),
        
        # Google (só se configurado)
        ("google", "gemini-1.5-flash", "Teste Google Gemini"),
        
        # OpenRouter (só se configurado)  
        ("openrouter", "openai/gpt-4o-mini", "Teste OpenRouter"),
        
        # DeepSeek (só se configurado)
        ("deepseek", "deepseek-chat", "Teste DeepSeek"),
    ]
    
    results = []
    
    for provider, model, message in tests:
        print(f"\\n🧪 Testando {provider} com modelo {model}...")
        
        try:
            result = manager.generate_response(
                messages=[{"role": "user", "content": message}],
                provider_name=provider,
                model=model
            )
            
            if result['success']:
                print(f"✅ {provider}: {result['response'][:100]}...")
                results.append((provider, model, True, None))
            else:
                print(f"❌ {provider}: {result['error']}")
                results.append((provider, model, False, result['error']))
                
        except Exception as e:
            print(f"❌ {provider}: Erro - {e}")
            results.append((provider, model, False, str(e)))
    
    # Resumo
    print("\\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    success_count = 0
    for provider, model, success, error in results:
        status = "✅" if success else "❌"
        print(f"{status} {provider} ({model})")
        if success:
            success_count += 1
    
    print(f"\\n🎯 Resultado: {success_count}/{len(results)} testes passaram")
    
    return success_count > 0

if __name__ == "__main__":
    success = test_providers()
    sys.exit(0 if success else 1)
'''
    
    with open('test_providers_fixed.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Script de teste criado: test_providers_fixed.py")

def main():
    """Executa todas as correções"""
    print("🚀 CORREÇÃO DO ROTEAMENTO DE PROVEDORES LLM")
    print("=" * 60)
    
    # 1. Corrigir roteamento
    print("1️⃣ Corrigindo roteamento de provedores...")
    fix_llm_routing()
    
    # 2. Criar teste
    print("\\n2️⃣ Criando script de teste...")
    create_provider_test()
    
    # 3. Verificar API Keys
    print("\\n3️⃣ Status das API Keys:")
    keys = {
        'OPENAI_API_KEY': 'OpenAI',
        'GOOGLE_API_KEY': 'Google Gemini', 
        'OPENROUTER_API_KEY': 'OpenRouter',
        'DEEPSEEK_API_KEY': 'DeepSeek'
    }
    
    configured = 0
    for env_var, name in keys.items():
        value = os.getenv(env_var)
        if value:
            print(f"✅ {name}: Configurada")
            configured += 1
        else:
            print(f"❌ {name}: NÃO configurada")
    
    print(f"\\n📊 Total: {configured}/{len(keys)} API Keys configuradas")
    
    # 4. Recomendações
    print("\\n" + "=" * 60)
    print("💡 PRÓXIMOS PASSOS:")
    print("🔄 Reinicie o servidor Streamlit")
    print("🧪 Execute: python test_providers_fixed.py")
    print("🌐 Teste na interface Multi-LLM")
    
    if configured < 2:
        print("\\n⚠️ RECOMENDAÇÃO:")
        print("Configure mais API Keys para testar outros provedores:")
        print("• OpenRouter: https://openrouter.ai/")
        print("• DeepSeek: https://platform.deepseek.com/")
        print("• Google AI: https://makersuite.google.com/")

if __name__ == "__main__":
    main() 