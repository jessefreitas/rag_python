-- =================================================================
-- Schema para o Banco de Dados de Agentes de IA (Versão 2)
-- Suporte a Multi-LLM e Feedback Individual
-- =================================================================

-- Requer a extensão pgvector: CREATE EXTENSION IF NOT EXISTS vector;
-- E a extensão pgcrypto para UUIDs: CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgvector;

-- ---------------------------------------------------------------------
-- Tabela 1: agentes
-- Armazena a configuração principal de cada agente.
-- ---------------------------------------------------------------------
CREATE TABLE agentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    system_prompt TEXT,
    model TEXT DEFAULT 'gpt-4o-mini',
    temperature NUMERIC(3, 2) CHECK (temperature BETWEEN 0 AND 2) DEFAULT 0.7,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE agentes IS 'Tabela central para armazenar a configuração e metadados de cada agente de IA.';

-- ---------------------------------------------------------------------
-- Tabela 2: documents
-- Repositório para todos os documentos e fontes de dados.
-- O conteúdo é chunked e vetorizado na tabela 'document_chunks'.
-- ---------------------------------------------------------------------
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agentes(id) ON DELETE CASCADE,
    file_name TEXT,
    source_type TEXT NOT NULL, -- 'pdf', 'url', 'txt', 'docx', etc.
    content_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE documents IS 'Armazena metadados de cada documento fonte de um agente.';
CREATE INDEX idx_docs_agent_id ON documents(agent_id);
CREATE UNIQUE INDEX idx_docs_hash ON documents(content_hash);

-- ---------------------------------------------------------------------
-- Tabela 3: document_chunks
-- Armazena os pedaços de texto (chunks) e seus vetores (embeddings).
-- ---------------------------------------------------------------------
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agentes(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL, -- Dimensão para text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE document_chunks IS 'Coração do RAG, armazena chunks e seus embeddings.';
CREATE INDEX idx_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_agent_id ON document_chunks(agent_id);

-- ---------------------------------------------------------------------
-- Tabela 4: conversations
-- Log de todas as conversas entre usuários e agentes.
-- ---------------------------------------------------------------------
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agentes(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE conversations IS 'Registra a entrada do usuário em uma conversa com um agente.';
CREATE INDEX idx_conversations_agent_id ON conversations(agent_id);

-- ---------------------------------------------------------------------
-- Tabela 5: llm_responses
-- Armazena as respostas dos LLMs para cada conversa.
-- ---------------------------------------------------------------------
CREATE TABLE llm_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    provider TEXT NOT NULL, -- Ex: 'openai', 'google_gemini', 'anthropic'
    model_used TEXT,
    response_text TEXT NOT NULL,
    tokens_used INTEGER,
    feedback SMALLINT CHECK (feedback IN (-1, 0, 1)) DEFAULT 0, -- -1: Ruim, 0: Neutro, 1: Bom
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE llm_responses IS 'Armazena cada resposta de um LLM, permitindo comparação e feedback individual.';
COMMENT ON COLUMN llm_responses.feedback IS 'Feedback do usuário: -1 para ruim, 0 para neutro, 1 para bom.';
CREATE INDEX idx_responses_conversation_id ON llm_responses(conversation_id); 