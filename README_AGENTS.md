# 🤖 Sistema de Agentes RAG

Sistema inteligente que integra agentes de IA com RAG (Retrieval-Augmented Generation) para criar assistentes autônomos e especializados.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Tipos de Agentes](#tipos-de-agentes)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Exemplos](#exemplos)
- [API](#api)
- [Deploy](#deploy)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O Sistema de Agentes RAG combina a potência dos agentes de IA com a precisão do RAG para criar assistentes inteligentes que podem:

- **Conversar naturalmente** usando conhecimento baseado em documentos
- **Realizar pesquisas** especializadas em grandes volumes de dados
- **Executar tarefas** complexas baseadas em conhecimento específico
- **Coordenar múltiplos agentes** para tarefas complexas
- **Integrar com RAGFlow** para funcionalidades avançadas

### 🚀 Principais Recursos

- 🤖 **Múltiplos tipos de agentes** (conversacional, pesquisa, executor)
- 🔄 **Sistema multi-agente** com coordenação inteligente
- 🧠 **Memória de conversação** para contexto contínuo
- 🔧 **Ferramentas integradas** para consulta RAG
- 📊 **Métricas de confiança** e performance
- 🎨 **Interface Streamlit** moderna e intuitiva
- 🔗 **Integração com RAGFlow** via API
- ⚡ **Performance otimizada** com cache e paralelização

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │   Sistema       │    │   Sistema       │
│   Streamlit     │◄──►│   Multi-Agente  │◄──►│   RAG           │
│   (agent_app.py)│    │                 │    │   (Local/API)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Agentes       │
                       │   Especializados│
                       │                 │
                       │ • Conversacional│
                       │ • Pesquisa      │
                       │ • Executor      │
                       │ • Personalizado │
                       └─────────────────┘
```

### Componentes Principais

1. **`agent_system.py`** - Sistema core de agentes
2. **`agent_app.py`** - Interface Streamlit
3. **`example_agents.py`** - Exemplos práticos
4. **`rag_system.py`** - Sistema RAG local
5. **`ragflow_client.py`** - Cliente RAGFlow

## 🤖 Tipos de Agentes

### 1. Agente Conversacional
- **Propósito**: Conversas naturais com conhecimento baseado em documentos
- **Características**: Amigável, contextual, informativo
- **Uso**: Chatbots, assistentes virtuais, suporte ao cliente

```python
from agent_system import ConversationalAgent

agent = ConversationalAgent(rag_system)
response = agent.process("Olá! Como você pode me ajudar?")
```

### 2. Agente de Pesquisa
- **Propósito**: Análise profunda e pesquisa em documentos
- **Características**: Analítico, detalhado, especializado
- **Uso**: Pesquisa acadêmica, análise de documentos, insights

```python
from agent_system import ResearchAgent

agent = ResearchAgent(rag_system)
response = agent.analyze_documents("Machine Learning")
```

### 3. Agente Executor
- **Propósito**: Execução de tarefas específicas baseadas em documentos
- **Características**: Prático, orientado a resultados, eficiente
- **Uso**: Automação, geração de relatórios, extração de dados

```python
from agent_system import TaskExecutorAgent

agent = TaskExecutorAgent(rag_system)
response = agent.execute_task("Crie um resumo sobre IA")
```

### 4. Sistema Multi-Agente
- **Propósito**: Coordenação inteligente entre múltiplos agentes
- **Características**: Roteamento automático, coordenação, escalabilidade
- **Uso**: Sistemas complexos, workflows automatizados

```python
from agent_system import MultiAgentSystem

system = MultiAgentSystem(rag_system)
response = system.process_with_coordination("Pesquise e analise sobre IA")
```

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- OpenAI API Key
- RAGFlow (opcional, para funcionalidades avançadas)

### Instalação Local

```bash
# Clonar o repositório
git clone <repository-url>
cd rag_python

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas chaves de API
```

### Dependências Adicionais

```bash
# Para agentes de IA
pip install langchain langchain-openai

# Para interface avançada
pip install streamlit plotly

# Para processamento assíncrono
pip install asyncio aiohttp
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# OpenAI (obrigatório)
OPENAI_API_KEY=your_openai_api_key

# RAGFlow (opcional)
RAGFLOW_BASE_URL=http://localhost:9380
RAGFLOW_API_KEY=your_ragflow_api_key

# Configurações do sistema
AGENT_MODEL=gpt-3.5-turbo
AGENT_TEMPERATURE=0.7
AGENT_MAX_ITERATIONS=5
```

### Configuração de Agentes

```python
from agent_system import AgentConfig

# Configuração personalizada
config = AgentConfig(
    name="Meu Agente",
    description="Agente personalizado para minhas necessidades",
    system_prompt="Você é um especialista em...",
    tools=["rag_query", "search_documents"],
    memory=True,
    temperature=0.5,
    model_name="gpt-4"
)
```

## 🚀 Uso

### Interface Streamlit

```bash
# Executar interface principal
streamlit run agent_app.py

# Executar interface integrada
streamlit run app_integrated.py
```

### Uso Programático

```python
from agent_system import MultiAgentSystem
from rag_system import RAGSystem

# Inicializar sistemas
rag_system = RAGSystem()
multi_agent = MultiAgentSystem(rag_system)

# Processar consulta
response = multi_agent.process_with_coordination(
    "Pesquise sobre machine learning e crie um resumo"
)

print(f"Resposta: {response.content}")
print(f"Confiança: {response.confidence}")
print(f"Agente usado: {response.metadata['selected_agent']}")
```

### Criação de Agente Personalizado

```python
from agent_system import AgentConfig, BaseAgent

# Configuração personalizada
config = AgentConfig(
    name="Agente Financeiro",
    description="Especialista em análise financeira",
    system_prompt="""Você é um especialista em finanças com vasto conhecimento 
    em análise de investimentos, mercado financeiro e economia. 
    Forneça análises precisas e recomendações baseadas em dados.""",
    tools=["rag_query", "search_documents"],
    memory=True,
    temperature=0.3
)

# Criar agente
agent = BaseAgent(config, rag_system)

# Usar agente
response = agent.process("Analise o mercado de ações brasileiro")
```

## 📚 Exemplos

### Exemplo Básico

```python
from agent_system import ConversationalAgent
from rag_system import RAGSystem

# Configurar
rag_system = RAGSystem()
agent = ConversationalAgent(rag_system)

# Conversar
response = agent.process("Explique sobre inteligência artificial")
print(response.content)
```

### Exemplo Avançado

```python
from agent_system import MultiAgentSystem
from ragflow_client import RAGFlowRAGSystem

# Usar RAGFlow
ragflow = RAGFlowRAGSystem(
    base_url="http://localhost:9380",
    api_key="your_key"
)

# Sistema multi-agente
system = MultiAgentSystem(ragflow)

# Processar tarefa complexa
response = system.process_with_coordination("""
    Pesquise sobre deep learning, analise os documentos encontrados 
    e gere um relatório executivo com recomendações
""")

print(f"Resultado: {response.content}")
```

### Executar Exemplos

```bash
# Executar todos os exemplos
python example_agents.py

# Executar exemplo específico
python -c "
from example_agents import example_conversational_agent
example_conversational_agent()
"
```

## 🔌 API

### Classe BaseAgent

```python
class BaseAgent:
    def __init__(self, config: AgentConfig, rag_system=None)
    def process(self, user_input: str) -> AgentResponse
    def _create_tools(self) -> List[Tool]
    def _create_agent(self)
```

### Classe MultiAgentSystem

```python
class MultiAgentSystem:
    def __init__(self, rag_system=None)
    def add_agent(self, name: str, agent: BaseAgent)
    def route_request(self, user_input: str) -> str
    def process_with_coordination(self, user_input: str) -> AgentResponse
    def get_agent_status(self) -> Dict[str, Any]
```

### Estrutura AgentResponse

```python
@dataclass
class AgentResponse:
    content: str                    # Resposta do agente
    actions_taken: List[str]        # Ações realizadas
    confidence: float               # Nível de confiança (0-1)
    sources: List[Dict]             # Fontes consultadas
    metadata: Dict                  # Metadados adicionais
```

## 🚀 Deploy

### Deploy Local

```bash
# Configurar ambiente
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run agent_app.py
```

### Deploy em VPS

```bash
# Usar script de deploy
chmod +x deploy_vps.sh
./deploy_vps.sh

# Ou deploy manual
# 1. Instalar dependências do sistema
# 2. Configurar Python e pip
# 3. Instalar dependências Python
# 4. Configurar variáveis de ambiente
# 5. Configurar systemd para auto-start
# 6. Configurar nginx como proxy reverso
```

### Deploy com Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "agent_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de API Key
```
❌ OpenAI API Key não configurada
```
**Solução**: Configure a variável `OPENAI_API_KEY` no arquivo `.env`

#### 2. Erro de Conexão RAGFlow
```
❌ Erro ao conectar com RAGFlow
```
**Solução**: Verifique se o RAGFlow está rodando e acessível

#### 3. Erro de Memória
```
❌ Erro de memória insuficiente
```
**Solução**: Reduza o número de documentos ou use chunking

#### 4. Performance Lenta
```
⚠️ Respostas lentas
```
**Soluções**:
- Use modelos menores (gpt-3.5-turbo em vez de gpt-4)
- Reduza o número de iterações
- Implemente cache
- Use processamento assíncrono

### Logs e Debug

```python
import logging

# Configurar logs detalhados
logging.basicConfig(level=logging.DEBUG)

# Verificar status dos agentes
system = MultiAgentSystem(rag_system)
status = system.get_agent_status()
print(status)
```

### Monitoramento

```python
# Métricas de performance
import time

start_time = time.time()
response = agent.process("teste")
execution_time = time.time() - start_time

print(f"Tempo: {execution_time:.2f}s")
print(f"Confiança: {response.confidence:.2f}")
```

## 📈 Próximos Passos

### Melhorias Planejadas

1. **Agentes Especializados**
   - Agente de Análise de Dados
   - Agente de Geração de Código
   - Agente de Tradução

2. **Funcionalidades Avançadas**
   - Processamento de imagens
   - Análise de sentimentos
   - Geração de gráficos

3. **Integrações**
   - Slack/Discord bots
   - APIs REST
   - Webhooks

4. **Otimizações**
   - Cache inteligente
   - Processamento paralelo
   - Modelos locais

### Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Faça commit e push
6. Abra um Pull Request

## 📞 Suporte

- **Documentação**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/seu-repo/issues)
- **Discord**: [Canal de Suporte](https://discord.gg/seu-canal)

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ para a comunidade de IA** 