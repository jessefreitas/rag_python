# RAG Python - Sistema de Retrieval-Augmented Generation

Este projeto implementa um sistema RAG (Retrieval-Augmented Generation) completo em Python, permitindo criar chatbots inteligentes que podem responder perguntas baseadas em documentos específicos.

## 🚀 Funcionalidades

- **Processamento de Documentos**: Suporte para PDF, DOCX, TXT e páginas web
- **Embeddings**: Geração de embeddings usando modelos de linguagem
- **Vector Database**: Armazenamento e busca semântica usando ChromaDB
- **Interface Web**: Interface interativa usando Streamlit
- **Integração OpenAI**: Conectividade com modelos GPT da OpenAI

## 📋 Pré-requisitos

- Python 3.8+
- Chave da API OpenAI
- Conexão com internet

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/jessefreitas/rag_python.git
cd rag_python

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com sua chave da OpenAI
```

## 🔧 Configuração

1. Crie um arquivo `.env` na raiz do projeto:
```
OPENAI_API_KEY=sua_chave_api_aqui
```

2. Adicione seus documentos na pasta `documents/`

## 🎯 Como Usar

### Interface Web (Recomendado)
```bash
streamlit run app.py
```

### Script Python
```python
from rag_system import RAGSystem

# Inicializar o sistema
rag = RAGSystem()

# Fazer uma pergunta
resposta = rag.query("Sua pergunta aqui")
print(resposta)
```

## 📊 Estrutura do Projeto

```
rag_python/
├── app.py                 # Interface Streamlit
├── rag_system.py          # Sistema RAG principal
├── document_loader.py     # Carregador de documentos
├── vector_store.py        # Gerenciamento do banco de vetores
├── documents/             # Pasta para documentos
├── requirements.txt       # Dependências
├── .env.example          # Exemplo de configuração
└── README.md             # Este arquivo
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📚 Documentação

- [Configuração de Provedores LLM](PROVIDERS_SETUP.md)
- [Sistema Multi-LLM](MULTI_LLM_FEATURE.md)
- [Sistema de Agentes](README_AGENTS.md)
- [Sistema Integrado](README_INTEGRATED.md)
- [Sistema Web](README_WEB_SYSTEM.md)
- [Fluxo de Documentos](FLUXO_DOCUMENTOS.md)
- [🔒 Isolamento de Segurança](SECURITY_ISOLATION.md)
- [🔧 Solução de Problemas](TROUBLESHOOTING.md)
- [📋 Log de Implementação](IMPLEMENTATION_LOG.md)
- [🔌 Extensão Chrome Isolada](CHROME_EXTENSION_ISOLATED.md)

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Jessé Freitas**
- GitHub: [@jessefreitas](https://github.com/jessefreitas) 