# Configuração de Provedores de IA

Este documento explica como configurar os diferentes provedores de IA suportados pelo sistema RAG Python.

## Provedores Suportados

### 1. OpenAI (Recomendado para iniciantes)

**Vantagens:**
- API estável e bem documentada
- Modelos de alta qualidade (GPT-3.5, GPT-4)
- Suporte oficial do LangChain

**Configuração:**
1. Acesse [OpenAI Platform](https://platform.openai.com/api-keys)
2. Crie uma conta e obtenha sua API key
3. Configure a variável de ambiente:

```bash
# .env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Modelos disponíveis:**
- `gpt-3.5-turbo` (padrão, econômico)
- `gpt-4` (mais avançado)
- `gpt-4-turbo` (versão mais recente)

### 2. OpenRouter (Acesso Unificado)

**Vantagens:**
- Acesso a múltiplos provedores através de uma única API
- Preços competitivos
- Modelos da OpenAI, Anthropic, Google, etc.
- Fallback automático entre provedores

**Configuração:**
1. Acesse [OpenRouter](https://openrouter.ai/keys)
2. Crie uma conta e obtenha sua API key
3. Configure a variável de ambiente:

```bash
# .env
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
```

**Modelos disponíveis:**
- `openai/gpt-4o-mini` (econômico)
- `openai/gpt-4o` (avançado)
- `anthropic/claude-3-haiku` (rápido)
- `anthropic/claude-3-sonnet` (equilibrado)
- `google/gemini-1.5-flash` (Google)

### 3. Google Gemini

**Vantagens:**
- Modelos do Google
- Boa performance em tarefas específicas
- Preços competitivos

**Configuração:**
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma conta e obtenha sua API key
3. Configure a variável de ambiente:

```bash
# .env
GOOGLE_GEMINI_API_KEY=your-gemini-api-key-here
```

**Modelos disponíveis:**
- `gemini-1.5-flash` (rápido)
- `gemini-1.5-pro` (avançado)

## Configuração Completa

### Arquivo .env

```bash
# =================================================================
# PROVEDORES DE IA
# =================================================================

# OpenAI (recomendado para começar)
OPENAI_API_KEY=sk-your-openai-api-key-here

# OpenRouter (acesso unificado)
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here

# Google Gemini
GOOGLE_GEMINI_API_KEY=your-gemini-api-key-here

# =================================================================
# BANCO DE DADOS (para sistema web)
# =================================================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_python_db
DB_USER=rag_user
DB_PASSWORD=your_secure_password

# =================================================================
# CONFIGURAÇÕES AVANÇADAS
# =================================================================
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_MODEL=gpt-3.5-turbo
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1000
```

### Estratégias de Configuração

#### Estratégia 1: Apenas OpenAI (Simples)
```bash
OPENAI_API_KEY=sk-abc123...
# Comente ou remova as outras chaves
```

#### Estratégia 2: OpenAI + OpenRouter (Recomendado)
```bash
OPENAI_API_KEY=sk-abc123...
OPENROUTER_API_KEY=sk-or-def456...
# O sistema usará OpenRouter por padrão se disponível
```

#### Estratégia 3: Todos os Provedores (Avançado)
```bash
OPENAI_API_KEY=sk-abc123...
OPENROUTER_API_KEY=sk-or-def456...
GOOGLE_GEMINI_API_KEY=AIzaSy...
# Máxima flexibilidade na interface web
```

## Uso na Interface Web

### Seleção de Provedor

1. Acesse a página de criação/edição de agentes
2. No campo "Provedor de IA", selecione o provedor desejado
3. O sistema carregará automaticamente os modelos disponíveis
4. Escolha o modelo e configure os parâmetros

### Troca de Provedor

Você pode trocar o provedor de um agente existente:

1. Edite o agente
2. Selecione um novo provedor
3. Escolha um modelo compatível
4. Salve as alterações

## Comparação de Custos

### OpenAI
- GPT-3.5-turbo: ~$0.002/1K tokens
- GPT-4: ~$0.03/1K tokens
- GPT-4-turbo: ~$0.01/1K tokens

### OpenRouter
- GPT-4o-mini: ~$0.00015/1K tokens
- Claude-3-haiku: ~$0.00025/1K tokens
- Gemini-1.5-flash: ~$0.000075/1K tokens

### Google Gemini
- Gemini-1.5-flash: ~$0.000075/1K tokens
- Gemini-1.5-pro: ~$0.0035/1K tokens

## Troubleshooting

### Erro: "Nenhum provedor de IA configurado"

**Solução:**
1. Verifique se pelo menos uma API key está configurada
2. Confirme que o arquivo `.env` está no diretório raiz
3. Reinicie a aplicação após configurar as variáveis

### Erro: "Provedor não disponível"

**Solução:**
1. Verifique se a API key está correta
2. Confirme se o provedor está funcionando
3. Tente usar outro provedor como fallback

### Erro: "Modelo não encontrado"

**Solução:**
1. Verifique se o modelo está disponível no provedor
2. Tente usar um modelo mais comum (ex: gpt-3.5-turbo)
3. Atualize a lista de modelos na interface

## Dicas de Uso

### Para Desenvolvimento
- Use OpenAI para testes iniciais
- Configure OpenRouter para acesso a múltiplos modelos
- Mantenha as chaves seguras (não commite no Git)

### Para Produção
- Use múltiplos provedores para redundância
- Configure fallbacks automáticos
- Monitore o uso e custos de cada provedor

### Para Economia
- Use modelos menores para tarefas simples
- Configure limites de tokens
- Monitore o uso através das estatísticas

## Próximos Passos

1. Configure pelo menos um provedor
2. Teste a criação de agentes
3. Explore diferentes modelos
4. Configure o banco de dados para o sistema web
5. Personalize os prompts dos agentes 