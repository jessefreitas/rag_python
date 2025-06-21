# 📄 Fluxo de Documentos no Sistema RAG

## 🔄 Visão Geral do Processo

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Documentos    │───►│   Document      │───►│   Vector Store  │───►│   RAG System    │
│   (PDF, DOCX,   │    │   Loader        │    │   (ChromaDB)    │    │   (Respostas)   │
│   TXT, Web)     │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Chunks        │    │   Embeddings    │
                       │   (Pedaços)     │    │   (Vetores)     │
                       └─────────────────┘    └─────────────────┘
```

## 📁 Onde os Documentos são Armazenados

### 1. **Arquivos Originais**
- **Localização**: Pasta `documents/` (ou qualquer pasta que você especificar)
- **Formatos Suportados**: PDF, DOCX, TXT, páginas web
- **Status**: Arquivos originais permanecem inalterados

### 2. **Banco de Vetores (ChromaDB)**
- **Localização**: Pasta `./vector_db/` (padrão)
- **Conteúdo**: 
  - Embeddings (vetores) dos documentos
  - Metadados dos documentos
  - Índices para busca rápida
- **Status**: Dados processados e indexados

### 3. **Estrutura de Pastas**
```
rag_python/
├── documents/              # 📁 Documentos originais
│   ├── manual.pdf
│   ├── relatorio.docx
│   └── dados.txt
├── vector_db/              # 🗄️ Banco de vetores (ChromaDB)
│   ├── chroma.sqlite3      # Banco SQLite do ChromaDB
│   ├── index/              # Índices de busca
│   └── embeddings/         # Vetores dos documentos
├── rag_system.py           # Sistema principal
├── vector_store.py         # Gerenciador do banco
└── document_loader.py      # Carregador de documentos
```

## 🔄 Processo Detalhado

### Passo 1: Carregamento de Documentos
```python
# Exemplo de carregamento
rag_system = RAGSystem()
rag_system.load_documents(
    file_paths=["documents/manual.pdf"],
    directory_path="documents/",
    urls=["https://exemplo.com/documento"]
)
```

**O que acontece:**
1. Documentos são lidos da pasta `documents/`
2. Cada documento é processado pelo `DocumentLoader`
3. Documentos são divididos em chunks menores (pedaços)
4. Metadados são adicionados (fonte, tipo, etc.)

### Passo 2: Processamento e Indexação
```python
# Internamente no sistema
documents = document_loader.load_document("manual.pdf")
# Resultado: Lista de chunks com metadados

vector_store.add_documents(documents)
# Resultado: Chunks são convertidos em embeddings e armazenados
```

**O que acontece:**
1. Cada chunk é convertido em embedding (vetor)
2. Embeddings são armazenados no ChromaDB
3. Índices são criados para busca rápida
4. Metadados são preservados

### Passo 3: Consulta e Resposta
```python
# Quando você faz uma pergunta
response = rag_system.query("Como funciona o sistema?")
```

**O que acontece:**
1. Sua pergunta é convertida em embedding
2. Sistema busca chunks similares no ChromaDB
3. Chunks relevantes são recuperados
4. GPT gera resposta baseada nos chunks
5. Resposta é retornada com fontes

## 🗄️ Banco de Dados: ChromaDB

### Características do ChromaDB:
- **Tipo**: Banco de vetores (vector database)
- **Armazenamento**: Local (pasta `vector_db/`)
- **Formato**: SQLite + arquivos de índice
- **Função**: Armazenar embeddings e permitir busca por similaridade

### Estrutura Interna:
```
vector_db/
├── chroma.sqlite3          # Banco principal
├── index/                  # Índices de busca
│   ├── embeddings.idx      # Índice de embeddings
│   └── metadata.idx        # Índice de metadados
└── embeddings/             # Vetores dos documentos
    ├── embedding_1.vec
    ├── embedding_2.vec
    └── ...
```

## 📊 Exemplo Prático

### 1. Adicionar Documentos
```python
from rag_system import RAGSystem

# Inicializar sistema
rag = RAGSystem()

# Carregar documentos
rag.load_documents(
    directory_path="./documents"  # Pasta com seus documentos
)
```

### 2. Verificar Status
```python
# Ver informações do banco
info = rag.vector_store.get_collection_info()
print(f"Documentos no banco: {info['document_count']}")
print(f"Localização: {info['persist_directory']}")
```

### 3. Fazer Consultas
```python
# Consultar o sistema
response = rag.query("Explique sobre machine learning")
print(f"Resposta: {response['answer']}")
print(f"Fontes: {response['sources']}")
```

## 🔧 Configurações Importantes

### Localização do Banco de Vetores
```python
# Padrão
rag = RAGSystem(persist_directory="./vector_db")

# Personalizado
rag = RAGSystem(persist_directory="/caminho/personalizado/vector_db")
```

### Tamanho dos Chunks
```python
# Chunks menores = mais precisão, menos contexto
rag = RAGSystem(chunk_size=500, chunk_overlap=100)

# Chunks maiores = mais contexto, menos precisão
rag = RAGSystem(chunk_size=2000, chunk_overlap=400)
```

## 🚀 Comandos Úteis

### Verificar Documentos Carregados
```python
# Ver quantos documentos estão no banco
info = rag.vector_store.get_collection_info()
print(f"Total de documentos: {info['document_count']}")

# Listar fontes dos documentos
sources = rag.vector_store.get_document_sources()
for source in sources:
    print(f"- {source}")
```

### Limpar Banco
```python
# Remover todos os documentos
rag.vector_store.delete_collection()

# Ou resetar todo o sistema
rag.reset_system()
```

### Backup e Restore
```python
# O banco está na pasta vector_db/
# Para backup, copie toda a pasta
# Para restore, substitua a pasta
```

## ❓ Perguntas Frequentes

### Q: Os documentos originais são modificados?
**A**: Não! Os arquivos originais permanecem inalterados na pasta `documents/`. Apenas os embeddings são armazenados no banco.

### Q: Posso usar outro banco de dados?
**A**: Sim! O sistema usa ChromaDB por padrão, mas pode ser adaptado para outros bancos de vetores como Pinecone, Weaviate, etc.

### Q: Onde ficam os embeddings?
**A**: No ChromaDB, que é armazenado localmente na pasta `vector_db/`. Os embeddings são vetores numéricos que representam o significado dos textos.

### Q: Como adicionar novos documentos?
**A**: Simplesmente coloque os arquivos na pasta `documents/` e execute `rag.load_documents()` novamente.

### Q: O banco é persistente?
**A**: Sim! O ChromaDB salva automaticamente todos os dados. Mesmo que você reinicie o sistema, os documentos continuam disponíveis.

## 🎯 Resumo

1. **Documentos originais** → Pasta `documents/`
2. **Processamento** → Divididos em chunks
3. **Embeddings** → Convertidos em vetores
4. **Armazenamento** → ChromaDB (pasta `vector_db/`)
5. **Consultas** → Busca por similaridade + GPT
6. **Respostas** → Baseadas nos documentos originais

O sistema mantém seus documentos originais seguros e cria uma base de conhecimento inteligente para consultas rápidas e precisas! 