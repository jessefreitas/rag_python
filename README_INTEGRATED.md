# 🤖 RAG Python + RAGFlow - Sistema Integrado

Este projeto oferece uma integração completa entre o **RAG Python** (sistema local simples) e o **RAGFlow** (plataforma robusta via API), permitindo escolher o backend mais adequado para suas necessidades.

## 🎯 Visão Geral

### RAG Python (Local)
- **Tipo**: Sistema local simples
- **Complexidade**: Baixa
- **Recursos**: Básicos mas eficientes
- **Ideal para**: POCs, desenvolvimento, uso pessoal
- **Tecnologias**: LangChain, OpenAI, ChromaDB, Streamlit

### RAGFlow (API)
- **Tipo**: Plataforma distribuída robusta
- **Complexidade**: Alta
- **Recursos**: Avançados e escaláveis
- **Ideal para**: Produção, empresas, múltiplos usuários
- **Tecnologias**: Docker, API REST, processamento avançado

## 🚀 Instalação Rápida

### 1. Clone o projeto
```bash
git clone https://github.com/jessefreitas/rag_python.git
cd rag_python
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure a API key
```bash
cp env.example .env
# Edite o arquivo .env com sua chave da OpenAI
```

### 4. Execute o sistema integrado
```bash
streamlit run app_integrated.py
```

## 🌐 Deploy na VPS

Para deploy completo na VPS com ambos os sistemas:

```bash
# 1. Conecte na VPS
ssh root@5.78.79.6

# 2. Execute o script de deploy
wget https://raw.githubusercontent.com/jessefreitas/rag_python/main/deploy_vps.sh
chmod +x deploy_vps.sh
./deploy_vps.sh
```

### URLs após deploy:
- **Interface Integrada**: http://5.78.79.6:8501
- **RAGFlow Web**: http://5.78.79.6:8000
- **RAG Python Original**: http://5.78.79.6:8501 (seletor de backend)

## 📁 Estrutura do Projeto

```
rag_python/
├── app.py                 # Interface original (RAG Python)
├── app_integrated.py      # Interface integrada (ambos sistemas)
├── rag_system.py          # Sistema RAG Python
├── ragflow_client.py      # Cliente para RAGFlow
├── document_loader.py     # Carregador de documentos
├── vector_store.py        # Banco de vetores
├── example.py             # Exemplo RAG Python
├── example_integrated.py  # Exemplo integrado
├── deploy_vps.sh          # Script de deploy
├── requirements.txt       # Dependências
├── documents/             # Pasta para documentos
└── README_INTEGRATED.md   # Esta documentação
```

## 🔧 Como Usar

### Interface Integrada (Recomendado)

1. **Execute a interface integrada**:
   ```bash
   streamlit run app_integrated.py
   ```

2. **Escolha o backend**:
   - **RAG Python**: Sistema local simples
   - **RAGFlow**: Sistema robusto via API

3. **Configure as conexões**:
   - Para RAG Python: Configure sua API key da OpenAI
   - Para RAGFlow: Configure a URL da API (padrão: http://localhost:8000)

4. **Use normalmente**: A interface funciona igual para ambos os sistemas

### Via Código Python

```python
from rag_system import RAGSystem
from ragflow_client import RAGFlowRAGSystem

# Usar RAG Python local
rag_local = RAGSystem()
response = rag_local.query("O que é IA?")

# Usar RAGFlow via API
rag_flow = RAGFlowRAGSystem("http://localhost:8000", "minha_colecao")
response = rag_flow.query("O que é IA?")
```

## 🔄 Comparação dos Sistemas

| Característica | RAG Python | RAGFlow |
|----------------|------------|---------|
| **Tipo** | Local | Distribuído |
| **Complexidade** | Baixa | Alta |
| **Recursos** | Básicos | Avançados |
| **Escalabilidade** | Limitada | Alta |
| **Manutenção** | Simples | Complexa |
| **Custo** | Baixo | Médio/Alto |
| **Ideal para** | POCs, desenvolvimento | Produção, empresas |

## 🎮 Exemplos de Uso

### Exemplo 1: Chat Simples
```python
from ragflow_client import RAGFlowRAGSystem

# Inicializar com RAGFlow
rag = RAGFlowRAGSystem("http://localhost:8000", "meus_docs")

# Fazer perguntas
response = rag.query("O que é inteligência artificial?")
print(response["answer"])
```

### Exemplo 2: Upload de Documentos
```python
# Upload para RAG Python
rag_local = RAGSystem()
rag_local.load_documents(file_paths=["documento.pdf"])

# Upload para RAGFlow
rag_flow = RAGFlowRAGSystem("http://localhost:8000", "colecao")
rag_flow.load_documents(file_paths=["documento.pdf"])
```

### Exemplo 3: Busca de Documentos
```python
# Busca em RAG Python
results = rag_local.search_similar_documents("machine learning", k=5)

# Busca em RAGFlow
results = rag_flow.search_similar_documents("machine learning", k=5)
```

## 🛠️ Configuração Avançada

### Configurar RAGFlow

1. **Instalar RAGFlow**:
   ```bash
   git clone https://github.com/infiniflow/ragflow.git /opt/ragflow
   cd /opt/ragflow/docker
   cp service_conf.yaml.template service_conf.yaml
   ```

2. **Configurar API key**:
   ```yaml
   # service_conf.yaml
   llm:
     provider: openai
     api_key: sua_chave_aqui
   ```

3. **Iniciar RAGFlow**:
   ```bash
   docker-compose up -d
   ```

### Configurar RAG Python

1. **Variáveis de ambiente**:
   ```bash
   # .env
   OPENAI_API_KEY=sua_chave_aqui
   OPENAI_MODEL=gpt-3.5-turbo
   EMBEDDING_MODEL=text-embedding-ada-002
   ```

2. **Configurações avançadas**:
   ```python
   rag = RAGSystem(
       model_name="gpt-4",
       temperature=0.7,
       max_tokens=2000,
       chunk_size=1000,
       chunk_overlap=200
   )
   ```

## 📊 Monitoramento

### Comandos úteis na VPS:
```bash
# Status dos serviços
rag-status

# Backup dos dados
rag-backup

# Atualizar sistemas
rag-update

# Logs do RAG Python
journalctl -u rag-python -f

# Logs do RAGFlow
docker-compose logs -f
```

### Verificar saúde dos sistemas:
```bash
# RAG Python
curl http://localhost:8501

# RAGFlow
curl http://localhost:8000/health
```

## 🔒 Segurança

### Configurações recomendadas:
- **Firewall**: Apenas portas necessárias (SSH, 80, 443, 8501, 8000)
- **HTTPS**: Configure SSL/TLS para produção
- **Autenticação**: Implemente login se necessário
- **Backup**: Configure backups automáticos
- **Logs**: Monitore logs regularmente

### Variáveis de ambiente sensíveis:
```bash
# Nunca commite estas chaves
OPENAI_API_KEY=sua_chave_aqui
RAGFLOW_API_KEY=sua_chave_aqui
```

## 🐛 Solução de Problemas

### RAG Python não funciona:
```bash
# Verificar API key
echo $OPENAI_API_KEY

# Verificar dependências
pip install -r requirements.txt

# Verificar logs
streamlit run app.py --logger.level debug
```

### RAGFlow não conecta:
```bash
# Verificar se está rodando
docker ps | grep ragflow

# Verificar logs
docker-compose logs

# Verificar configuração
cat service_conf.yaml
```

### Interface não carrega:
```bash
# Verificar porta
netstat -tlnp | grep 8501

# Verificar firewall
ufw status

# Reiniciar serviço
systemctl restart rag-python
```

## 📈 Performance

### Otimizações para RAG Python:
- Use chunks menores para melhor precisão
- Ajuste temperatura para controlar criatividade
- Use modelos mais rápidos para desenvolvimento

### Otimizações para RAGFlow:
- Configure recursos adequados no Docker
- Use GPU se disponível
- Configure cache e persistência

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Teste com ambos os sistemas
5. Abra um Pull Request

## 📞 Suporte

- **Issues**: https://github.com/jessefreitas/rag_python/issues
- **Documentação**: README.md e DOCUMENTATION.md
- **Exemplos**: example.py e example_integrated.py

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido por Jessé Freitas**  
**GitHub**: [@jessefreitas](https://github.com/jessefreitas) 