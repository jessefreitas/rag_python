# Sistema RAG com Agentes de IA

Um sistema completo de Retrieval-Augmented Generation (RAG) com agentes de IA, interface web e suporte a múltiplos provedores de LLM.

## 🚀 Funcionalidades Principais

### 🤖 Agentes de IA
- **Agentes Especializados**: Conversacional, Pesquisa, Executor de Tarefas
- **Agentes Customizados**: Configuráveis com prompts e parâmetros específicos
- **Agentes Multi-LLM**: Compare respostas de diferentes provedores em tempo real
- **Memória de Conversação**: Contexto mantido entre interações
- **Sistema de Feedback**: Avalie a qualidade das respostas

### 📚 Sistema RAG
- **Upload de Documentos**: PDF, DOCX, TXT, PPTX, XLSX
- **Processamento Automático**: Extração e indexação de conteúdo
- **Busca Semântica**: Encontre informações relevantes nos documentos
- **Respostas Contextualizadas**: Baseadas no conhecimento dos documentos

### 🌐 Interface Web
- **Dashboard Interativo**: Estatísticas e monitoramento
- **Gerenciamento de Agentes**: Criação, edição e exclusão
- **Chat em Tempo Real**: Interface conversacional intuitiva
- **Comparação Multi-LLM**: Visualize respostas lado a lado
- **Sistema de Avaliação**: Like/dislike para feedback

### 🔌 Múltiplos Provedores de IA
- **OpenAI**: GPT-3.5, GPT-4, GPT-4o Mini
- **OpenRouter**: Acesso a múltiplos modelos
- **Google Gemini**: Modelos do Google
- **Anthropic Claude**: Modelos Claude
- **Interface Unificada**: Troque entre provedores facilmente

## 🆕 Nova Funcionalidade: Comparação Multi-LLM

### ✨ Comparação em Tempo Real
- **Múltiplos LLMs Simultâneos**: Compare respostas de diferentes provedores
- **Interface Visual**: Respostas lado a lado com identificação clara
- **Estatísticas de Comparação**: Tamanho, unicidade e diferenças
- **Seleção Flexível**: Escolha quais provedores usar

### 🎯 Como Usar
1. **Ative o Modo Multi-LLM**: Marque a caixa "Comparar Múltiplos LLMs"
2. **Selecione Provedores**: Escolha quais LLMs comparar
3. **Faça sua Pergunta**: Digite normalmente
4. **Compare Respostas**: Veja todas as respostas lado a lado
5. **Avalie**: Use os botões de feedback para cada resposta

### 📊 Benefícios
- **Melhor Qualidade**: Identifique qual LLM oferece melhores respostas
- **Otimização de Custos**: Compare performance vs. custo
- **Flexibilidade**: Troque entre provedores conforme necessário
- **Análise Comparativa**: Entenda diferenças entre modelos

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- PostgreSQL com extensão pgvector
- Contas nos provedores de IA desejados

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd rag_python
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as Variáveis de Ambiente
Crie um arquivo `.env` baseado no `env.example`:

```bash
# Banco de Dados PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/rag_system

# Provedores de IA
OPENAI_API_KEY=your_openai_key
OPENROUTER_API_KEY=your_openrouter_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key

# Configurações do Sistema
FLASK_SECRET_KEY=your_secret_key
```

### 4. Configure o Banco de Dados
```bash
# Execute o script SQL para criar as tabelas
psql -d your_database -f schema.sql
```

### 5. Inicialize o Sistema
```bash
python web_agent_manager.py
```

## 🚀 Uso Rápido

### 1. Acesse a Interface Web
```
http://localhost:5000
```

### 2. Crie um Agente
- Vá para "Agentes" → "Criar Novo Agente"
- Configure nome, descrição e parâmetros
- Selecione o provedor de IA desejado

### 3. Faça Upload de Documentos
- Acesse o agente criado
- Use a seção "Upload de Arquivos"
- Selecione documentos PDF, DOCX, etc.

### 4. Teste a Comparação Multi-LLM
- Ative o modo "Comparar Múltiplos LLMs"
- Selecione os provedores desejados
- Faça perguntas e compare as respostas

### 5. Monitore o Desempenho
- Use o dashboard para ver estatísticas
- Avalie respostas com o sistema de feedback
- Acompanhe métricas por agente

## 📖 Documentação Detalhada

### Configuração de Provedores
Veja [PROVIDERS_SETUP.md](PROVIDERS_SETUP.md) para configuração detalhada dos provedores de IA.

### Fluxo de Documentos
Veja [FLUXO_DOCUMENTOS.md](FLUXO_DOCUMENTOS.md) para entender como os documentos são processados.

### Sistema de Agentes
Veja [README_AGENTS.md](README_AGENTS.md) para detalhes sobre os tipos de agentes.

## 🧪 Testes

### Teste Multi-LLM
```bash
python test_multi_llm.py
```

### Teste de Provedores
```bash
python test_providers.py
```

### Teste do Sistema RAG
```bash
python test_server.py
```

## 📊 Estrutura do Projeto

```
rag_python/
├── web_agent_manager.py      # Servidor web principal
├── agent_system.py           # Sistema de agentes
├── rag_system.py            # Sistema RAG
├── llm_providers.py         # Gerenciador de provedores
├── database.py              # Conexão com banco de dados
├── vector_store.py          # Armazenamento de vetores
├── document_loader.py       # Carregamento de documentos
├── templates/               # Templates HTML
├── agent_uploads/           # Arquivos dos agentes
├── agent_vector_dbs/        # Bancos de vetores
├── requirements.txt         # Dependências Python
├── schema.sql              # Schema do banco de dados
└── docs/                   # Documentação
```

## 🔧 Configurações Avançadas

### Personalização de Agentes
```python
from agent_system import create_agent

# Agente customizado
agent = create_agent("custom", 
    name="Meu Agente",
    system_prompt="Você é um especialista em...",
    model_name="gpt-4",
    temperature=0.7,
    provider="openai"
)

# Agente multi-LLM
multi_agent = create_agent("multi_llm",
    name="Comparador",
    providers=["openai", "openrouter", "gemini"],
    model_name="gpt-3.5-turbo"
)
```

### Configuração de Provedores
```python
from llm_providers import llm_manager

# Configurar provedor ativo
llm_manager.set_active_provider("openai")

# Obter informações dos provedores
providers = llm_manager.get_provider_info()
models = llm_manager.get_provider_models("openai")
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

- **Issues**: Use o GitHub Issues para reportar bugs
- **Documentação**: Consulte os arquivos README específicos
- **Exemplos**: Veja a pasta `examples/` para casos de uso

## 🎯 Roadmap

- [ ] Suporte a mais formatos de documento
- [ ] Integração com mais provedores de IA
- [ ] Sistema de plugins para agentes
- [ ] API REST completa
- [ ] Interface mobile
- [ ] Análise avançada de performance
- [ ] Sistema de backup automático
- [ ] Integração com ferramentas externas

---

**Desenvolvido com ❤️ para facilitar o uso de IA em aplicações práticas**
