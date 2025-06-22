# Changelog - Sistema RAG Python

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Planejado
- Interface Streamlit para compliance LGPD
- Dashboard de monitoramento de privacidade
- Integração com Microsoft Presidio (PII detection avançada)
- API REST para sistema de privacidade

## [1.2.0] - 2025-06-22

### Added - Sistema de Privacidade e Compliance LGPD
- **privacy_system.py**: Sistema completo de privacidade e anonimização
  - Detecção automática de dados pessoais (CPF, CNPJ, email, telefone, RG, CEP)
  - Classificação de sensibilidade conforme LGPD
  - Múltiplos métodos de anonimização (pseudonimização, mascaramento, dados falsos)
  - Políticas de retenção automáticas (30 dias, 6 meses, 1 ano, 5 anos)
  - Trilha de auditoria completa para compliance
  - Soft delete e hard delete com logs
  - Limpeza automática baseada em políticas de retenção

- **agent_system_privacy.py**: Agentes com consciência de privacidade
  - PrivacyAwareAgent com 3 níveis (standard, high, maximum)
  - Processamento de documentos com verificação automática de dados pessoais
  - Controle de consentimento granular
  - Anonimização em tempo real durante processamento
  - Relatórios de compliance individuais por agente
  - Integração completa com sistema de auditoria

- **test_privacy_integration.py**: Testes completos do sistema integrado
  - Validação de todos os níveis de privacidade
  - Teste de processamento com dados pessoais reais
  - Verificação de consentimento e anonimização
  - Ciclo de vida completo dos dados
  - Integração Multi-LLM + Privacidade

### Dependencies Added
- `faker>=19.0.0`: Geração de dados falsos para anonimização
- `scrubadub>=2.0.0`: Detecção automática de PII
- `cryptography>=41.0.0`: Criptografia avançada

### LGPD Compliance Features
- Privacy by design nativo
- Consentimento granular por operação
- Direito ao esquecimento automatizado
- Portabilidade de dados com export anonimizado
- Auditoria completa de todas as operações
- Retenção automática conforme políticas definidas

## [1.1.0] - 2025-06-22

### Added
- **DeepSeek Provider**: Integração com modelos DeepSeek (deepseek-chat, deepseek-coder, deepseek-math)
- **Sistema Multi-LLM Expandido**: Comparação simultânea de múltiplos LLMs
- **Interface Streamlit Multi-LLM**: Nova interface (`app_multi_llm.py`) para comparação visual
- **Recomendação Inteligente**: Sistema que recomenda melhor LLM por tipo de tarefa
- **Métricas de Performance**: Comparação de tempo de resposta entre provedores
- **Configuração Flexível**: Suporte para múltiplas APIs simultâneas
- Arquivo de exemplo de configuração (`env_example.txt`)
- Script de teste expandido (`test_deepseek_multi_llm.py`)

### Changed
- **LLMProviderManager**: Métodos adicionais para comparação multi-LLM
- **Arquitetura Multi-LLM**: Suporte para fallback inteligente entre provedores
- Sistema de logs aprimorado para troubleshooting de APIs

### Technical Improvements
- Tratamento de erros robusto para APIs indisponíveis
- Medição de performance em tempo real
- Interface visual com gráficos de comparação
- Sistema de recomendação baseado em tipo de tarefa

### Planejado
- Sistema de privacidade e anonimização de dados
- Compliance LGPD automático
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