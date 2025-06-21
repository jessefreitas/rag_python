# Documentação Técnica - Sistema RAG Python

## 📋 Visão Geral

O Sistema RAG Python é uma implementação completa de Retrieval-Augmented Generation que permite criar chatbots inteligentes capazes de responder perguntas baseadas em documentos específicos.

## 🏗️ Arquitetura do Sistema

### Componentes Principais

1. **DocumentLoader** (`document_loader.py`)
   - Responsável pelo carregamento e processamento de documentos
   - Suporta múltiplos formatos: PDF, DOCX, TXT, páginas web

2. **VectorStore** (`vector_store.py`)
   - Gerencia o banco de dados de vetores usando ChromaDB
   - Realiza operações de busca semântica

3. **RAGSystem** (`rag_system.py`)
   - Componente principal que integra todos os módulos
   - Gerencia o fluxo de processamento de perguntas

4. **Interface Web** (`app.py`)
   - Interface Streamlit para interação com o sistema

## 🔧 Tecnologias Utilizadas

- **LangChain**: Framework para aplicações de IA
- **OpenAI GPT**: Modelos de linguagem para geração de respostas
- **ChromaDB**: Banco de dados de vetores
- **Streamlit**: Interface web interativa

## 🚀 Como Usar

### Instalação
```bash
pip install -r requirements.txt
```

### Configuração
```bash
cp env.example .env
# Edite o arquivo .env com sua chave da OpenAI
```

### Execução
```bash
# Interface web
streamlit run app.py

# Exemplo via Python
python example.py
```

## 📁 Estrutura do Projeto

```
rag_python/
├── app.py                 # Interface web
├── rag_system.py          # Sistema RAG principal
├── document_loader.py     # Carregador de documentos
├── vector_store.py        # Banco de vetores
├── example.py             # Exemplo de uso
├── requirements.txt       # Dependências
├── documents/             # Pasta para documentos
└── README.md             # Documentação
```

## 🎯 Funcionalidades

- ✅ Carregamento de PDF, DOCX, TXT e páginas web
- ✅ Processamento e indexação de documentos
- ✅ Busca semântica
- ✅ Geração de respostas baseadas no contexto
- ✅ Interface web interativa
- ✅ Configuração flexível de modelos

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no GitHub. 