# 🌐 Sistema Web de Gerenciamento de Agentes RAG

Sistema web completo para criar, gerenciar e interagir com agentes de IA especializados, cada um com sua própria base de conhecimento.

## 🎯 Visão Geral

O sistema web permite:
- **Criar agentes personalizados** com prompts específicos
- **Upload de documentos** para pastas específicas de cada agente
- **Chat individual** com cada agente baseado em seus documentos
- **Gerenciamento completo** via interface web intuitiva
- **Isolamento de conhecimento** - cada agente pesquisa apenas em seus documentos

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │   Flask Web     │    │   Agent         │
│   Web (HTML)    │◄──►│   Server        │◄──►│   Manager       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   API Endpoints │    │   Agent         │
                       │   (REST)        │    │   Storage       │
                       └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Per-Agent     │
                                              │   RAG Systems   │
                                              └─────────────────┘
```

## 📁 Estrutura de Pastas

```
rag_python/
├── web_agent_manager.py          # Servidor Flask principal
├── templates/                    # Templates HTML
│   ├── index.html               # Dashboard principal
│   ├── agents.html              # Gerenciamento de agentes
│   └── agent_detail.html        # Detalhes do agente
├── agent_uploads/               # Uploads por agente
│   ├── [agent-id-1]/           # Documentos do agente 1
│   └── [agent-id-2]/           # Documentos do agente 2
├── agent_vector_dbs/            # Bancos de vetores por agente
│   ├── [agent-id-1]/           # ChromaDB do agente 1
│   └── [agent-id-2]/           # ChromaDB do agente 2
├── agents_config.json           # Configuração dos agentes
└── requirements_web.txt         # Dependências do sistema web
```

## 🚀 Instalação e Configuração

### 1. Instalar Dependências

```bash
# Instalar dependências do sistema web
pip install -r requirements_web.txt

# Ou instalar manualmente
pip install flask flask-cors werkzeug
```

### 2. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cp env.example .env

# Editar .env com suas chaves
OPENAI_API_KEY=sua_chave_openai_aqui
```

### 3. Executar o Sistema

```bash
# Executar servidor web
python web_agent_manager.py

# Acessar no navegador
# http://localhost:5000
```

## 🎨 Interface Web

### Dashboard Principal (`/`)
- **Visão geral** de todos os agentes
- **Estatísticas** do sistema
- **Chat rápido** com qualquer agente
- **Acesso direto** para gerenciamento

### Gerenciamento de Agentes (`/agents`)
- **Criar novos agentes** com formulário completo
- **Editar agentes** existentes
- **Configurar prompts** personalizados
- **Definir parâmetros** (modelo, temperatura, etc.)

### Detalhes do Agente (`/agent/<id>`)
- **Upload de documentos** via drag & drop
- **Chat individual** com o agente
- **Visualizar documentos** carregados
- **Configurações** do agente

## 🤖 Criação de Agentes

### 1. Informações Básicas
```json
{
  "name": "Agente Financeiro",
  "description": "Especialista em análise financeira e mercado",
  "system_prompt": "Você é um especialista em finanças..."
}
```

### 2. Configurações Avançadas
```json
{
  "model_name": "gpt-3.5-turbo",
  "temperature": 0.3,
  "max_iterations": 5,
  "memory": true,
  "tools": ["rag_query", "search_documents"]
}
```

### 3. Exemplos de Prompts

#### Agente Financeiro
```
Você é um especialista em finanças com vasto conhecimento em análise de investimentos, 
mercado financeiro e economia. Forneça análises precisas e recomendações baseadas em dados. 
Sempre cite fontes e seja conservador em suas estimativas.
```

#### Agente Jurídico
```
Você é um advogado especializado em direito civil e comercial. Forneça orientações 
jurídicas baseadas na legislação brasileira. Sempre mencione que suas respostas são 
informativas e não substituem consulta profissional.
```

#### Agente Médico
```
Você é um médico especialista em diagnóstico e tratamento. Forneça informações médicas 
baseadas em evidências científicas. Sempre recomende consulta médica para casos específicos 
e não prescreva medicamentos.
```

## 📤 Upload de Documentos

### Formatos Suportados
- **PDF** (.pdf)
- **Word** (.docx, .doc)
- **Texto** (.txt)
- **PowerPoint** (.pptx)
- **Excel** (.xlsx)

### Processo de Upload
1. **Selecionar agente** na interface
2. **Arrastar arquivos** ou clicar para selecionar
3. **Upload automático** para pasta do agente
4. **Processamento** em chunks e embeddings
5. **Indexação** no banco de vetores específico

### Organização por Agente
```
agent_uploads/
├── agent-123/
│   ├── relatorio_financeiro.pdf
│   ├── balanco_2023.xlsx
│   └── analise_mercado.docx
└── agent-456/
    ├── manual_tecnico.pdf
    ├── especificacoes.txt
    └── documentacao.docx
```

## 🔌 API REST

### Endpoints Principais

#### Agentes
```http
GET    /api/agents              # Listar agentes
POST   /api/agents              # Criar agente
PUT    /api/agents/{id}         # Atualizar agente
DELETE /api/agents/{id}         # Deletar agente
```

#### Upload de Arquivos
```http
POST   /api/agents/{id}/upload  # Upload de arquivos
GET    /api/agents/{id}/files   # Listar arquivos
DELETE /api/agents/{id}/files/{filename}  # Deletar arquivo
```

#### Consultas
```http
POST   /api/agents/{id}/query   # Consultar agente
```

### Exemplos de Uso da API

#### Criar Agente
```bash
curl -X POST http://localhost:5000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente Teste",
    "description": "Agente para testes",
    "system_prompt": "Você é um agente de teste...",
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7
  }'
```

#### Upload de Arquivos
```bash
curl -X POST http://localhost:5000/api/agents/agent-id/upload \
  -F "files=@documento.pdf" \
  -F "files=@relatorio.docx"
```

#### Consultar Agente
```bash
curl -X POST http://localhost:5000/api/agents/agent-id/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Explique sobre machine learning"}'
```

## 🎯 Casos de Uso

### 1. Empresa com Múltiplos Departamentos
```
Agente Financeiro → Documentos financeiros
Agente RH → Políticas e procedimentos
Agente TI → Documentação técnica
Agente Legal → Contratos e regulamentos
```

### 2. Consultoria Especializada
```
Agente Marketing → Cases e estratégias
Agente Vendas → Propostas e negociações
Agente Operações → Processos e workflows
```

### 3. Educação
```
Agente Matemática → Exercícios e teoria
Agente História → Fatos históricos
Agente Literatura → Análises literárias
```

## 🔧 Configurações Avançadas

### Personalizar Configurações
```python
# No arquivo web_agent_manager.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
UPLOAD_FOLDER = 'agent_uploads'
AGENTS_CONFIG_FILE = 'agents_config.json'
```

### Configurar Banco de Dados
```python
# Cada agente tem seu próprio banco
vector_db_path = f"agent_vector_dbs/{agent_id}"
rag_system = RAGSystem(persist_directory=vector_db_path)
```

### Backup e Restore
```bash
# Backup de todos os agentes
tar -czf backup_agents.tar.gz agent_uploads/ agent_vector_dbs/ agents_config.json

# Restore
tar -xzf backup_agents.tar.gz
```

## 🚀 Deploy em Produção

### Usando Gunicorn
```bash
# Instalar gunicorn
pip install gunicorn

# Executar em produção
gunicorn -w 4 -b 0.0.0.0:5000 web_agent_manager:app
```

### Usando Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_web.txt .
RUN pip install -r requirements_web.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web_agent_manager:app"]
```

### Configurar Nginx
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoramento

### Logs do Sistema
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Métricas Importantes
- **Número de agentes** ativos
- **Documentos por agente**
- **Consultas realizadas**
- **Tempo de resposta**
- **Uso de memória**

## 🔒 Segurança

### Recomendações
1. **Autenticação** de usuários
2. **Validação** de arquivos uploadados
3. **Limite** de tamanho de arquivos
4. **HTTPS** em produção
5. **Backup** regular dos dados

### Implementar Autenticação
```python
from flask_login import LoginManager, login_required

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/agents')
@login_required
def agents_page():
    # Página protegida
    pass
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de Upload
```
❌ Arquivo muito grande
```
**Solução**: Aumentar `MAX_CONTENT_LENGTH` no Flask

#### 2. Agente não responde
```
❌ Erro de API OpenAI
```
**Solução**: Verificar `OPENAI_API_KEY` no arquivo `.env`

#### 3. Documentos não carregam
```
❌ Erro de permissão
```
**Solução**: Verificar permissões das pastas `agent_uploads/`

#### 4. Interface não carrega
```
❌ Erro de template
```
**Solução**: Verificar se pasta `templates/` existe

## 📈 Próximos Passos

### Melhorias Planejadas
1. **Autenticação** de usuários
2. **Compartilhamento** de agentes
3. **Templates** pré-configurados
4. **Análise** de uso e métricas
5. **Integração** com outros sistemas
6. **API** pública para terceiros

### Contribuição
1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Faça commit e push
6. Abra um Pull Request

---

**Sistema Web de Agentes RAG** - Organize, gerencie e interaja com seus agentes de IA de forma inteligente! 🚀 