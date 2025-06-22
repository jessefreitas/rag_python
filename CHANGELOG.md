# Changelog - Sistema RAG Python

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Planejado
- Sistema de testes automatizados
- CI/CD com GitHub Actions  
- Melhorias de observabilidade
- Documentação técnica expandida

## [1.0.0] - 2025-06-22

### Recuperado
- **Sistema RAG Principal** (`rag_system.py`) - Core do sistema com isolamento por agente
- **Gerenciador Multi-LLM** (`llm_providers.py`) - Suporte a múltiplos provedores de IA
- **Testes Multi-LLM** (`test_multi_llm.py`) - Validações do sistema multi-provedor

### Funcionalidades Existentes
- **Sistema de Agentes** - Agentes especializados com contexto isolado
  - Agente Cível configurado e funcional
  - Base de dados PostgreSQL
  - Upload e processamento de documentos
- **RAGFlow Integration** - Cliente para sistema RAGFlow via API
- **Interfaces Web** - Múltiplas interfaces Streamlit
  - `app.py` - Interface principal
  - `app_integrated.py` - Sistema integrado RAG + RAGFlow  
  - `agent_app.py` - Interface para agentes
- **Extensão Chrome** - Sistema de scraping web
- **Vector Store** - ChromaDB para armazenamento de embeddings
- **Document Loader** - Processamento de PDFs, DOCX, TXT

### Infraestrutura
- Base de dados PostgreSQL configurada
- Sistema de uploads organizado por agente
- Vector databases isolados por agente
- Configuração Docker preparada

### Segurança
- Isolamento completo entre agentes
- Validação de acesso por agent_id
- Sanitização de documentos

---

## Formato das Entradas

### Added
- Para novas funcionalidades

### Changed  
- Para mudanças em funcionalidades existentes

### Deprecated
- Para funcionalidades que serão removidas em breve

### Removed
- Para funcionalidades removidas

### Fixed
- Para correções de bugs

### Security
- Em caso de vulnerabilidades corrigidas 