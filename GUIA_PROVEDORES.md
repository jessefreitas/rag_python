# 🔧 GUIA DE CONFIGURAÇÃO DE PROVEDORES

## Como Obter as API Keys

### 1. Google Gemini
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave e adicione ao .env: `GOOGLE_GEMINI_API_KEY=sua-chave-aqui`

### 2. OpenRouter
1. Acesse: https://openrouter.ai/keys
2. Crie uma conta ou faça login
3. Clique em "Create Key"
4. Copie a chave e adicione ao .env: `OPENROUTER_API_KEY=sk-or-sua-chave-aqui`

### 3. DeepSeek
1. Acesse: https://platform.deepseek.com/api_keys
2. Crie uma conta ou faça login
3. Clique em "Create API Key"
4. Copie a chave e adicione ao .env: `DEEPSEEK_API_KEY=sk-sua-chave-aqui`

## Modelos Recomendados

### Para Uso Geral:
- OpenAI: gpt-4o-mini (econômico) ou gpt-4o (avançado)
- Google: gemini-1.5-flash (rápido) ou gemini-1.5-pro (avançado)
- OpenRouter: openai/gpt-4o ou anthropic/claude-3.5-sonnet
- DeepSeek: deepseek-chat (geral) ou deepseek-coder (programação)

## Teste da Configuração

Após configurar, execute:
```bash
python implementar_proximos_passos.py --teste-provedores
```
