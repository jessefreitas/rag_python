-- =================================================================
-- Schema para o Banco de Dados de Agentes de IA
-- Baseado no diagrama ERD para um sistema multi-agente com RAG
-- =================================================================

-- Requer a extensão pgvector: CREATE EXTENSION IF NOT EXISTS vector;
-- E a extensão pgcrypto para UUIDs: CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgvector;

-- ---------------------------------------------------------------------
-- Tabela 1: agentes
-- Armazena a configuração principal de cada agente.
-- ---------------------------------------------------------------------
CREATE TABLE agentes (
    id_agente UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_agente TEXT NOT NULL,
    descricao TEXT,
    system_prompt TEXT,
    modelo_base TEXT DEFAULT 'gpt-4o-mini',
    temperatura NUMERIC(3, 2) CHECK (temperatura BETWEEN 0 AND 2) DEFAULT 0.7,
    top_p NUMERIC(3, 2) CHECK (top_p BETWEEN 0 AND 1) DEFAULT 1.0,
    max_tokens INTEGER DEFAULT 1024,
    status TEXT DEFAULT 'ativo',
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE agentes IS 'Tabela central para armazenar a configuração e metadados de cada agente de IA.';
COMMENT ON COLUMN agentes.id_agente IS 'Identificador único universal para o agente.';
COMMENT ON COLUMN agentes.status IS 'Status do agente, ex: ativo, inativo, arquivado.';

-- ---------------------------------------------------------------------
-- Tabela 2: documentos_mestre
-- Repositório central para todos os documentos e fontes de dados.
-- ---------------------------------------------------------------------
CREATE TABLE documentos_mestre (
    id_doc UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_agente UUID NOT NULL REFERENCES agentes(id_agente) ON DELETE CASCADE,
    nome_arquivo TEXT,
    tipo_origem TEXT NOT NULL, -- 'pdf', 'url', 'txt', 'docx', etc.
    texto_bruto TEXT,
    hash_md5 TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE documentos_mestre IS 'Armazena o conteúdo bruto e metadados de cada documento fonte de um agente.';
COMMENT ON COLUMN documentos_mestre.hash_md5 IS 'Hash MD5 do conteúdo para evitar duplicatas.';
CREATE INDEX idx_docs_agente ON documentos_mestre(id_agente);
CREATE UNIQUE INDEX idx_docs_hash ON documentos_mestre(hash_md5);

-- ---------------------------------------------------------------------
-- Tabela 3: chunks_vetorizados
-- Armazena os pedaços de texto (chunks) e seus vetores (embeddings).
-- ---------------------------------------------------------------------
CREATE TABLE chunks_vetorizados (
    id_vetor UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_doc UUID NOT NULL REFERENCES documentos_mestre(id_doc) ON DELETE CASCADE,
    id_agente UUID NOT NULL REFERENCES agentes(id_agente) ON DELETE CASCADE,
    chunk_id INTEGER NOT NULL,
    chunk_texto TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL, -- Dimensão do vetor (ex: 768 para text-embedding-ada-002)
    modelo_embedding TEXT NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (id_doc, chunk_id)
);

COMMENT ON TABLE chunks_vetorizados IS 'Coração do sistema RAG, armazena os chunks de texto e seus embeddings vetoriais.';
CREATE INDEX idx_chunks_embedding ON chunks_vetorizados USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_agente ON chunks_vetorizados(id_agente);

-- ---------------------------------------------------------------------
-- Tabela 4: interacoes_usuarios
-- Log de todas as conversas entre usuários e agentes.
-- ---------------------------------------------------------------------
CREATE TABLE interacoes_usuarios (
    id_interacao UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_agente UUID NOT NULL REFERENCES agentes(id_agente) ON DELETE CASCADE,
    entrada_usuario TEXT NOT NULL,
    resposta_agente TEXT,
    embedding_entrada VECTOR(768),
    tokens_usados INTEGER,
    satisfacao SMALLINT CHECK (satisfacao BETWEEN 1 AND 5), -- Ex: 1 a 5
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE interacoes_usuarios IS 'Registra o histórico de conversas para fins de análise, debug e futuro fine-tuning.';
COMMENT ON COLUMN interacoes_usuarios.satisfacao IS 'Nota de feedback do usuário sobre a qualidade da resposta.';
CREATE INDEX idx_interacoes_agente ON interacoes_usuarios(id_agente);
CREATE INDEX idx_interacoes_embed ON interacoes_usuarios USING ivfflat (embedding_entrada vector_cosine_ops);

-- ---------------------------------------------------------------------
-- Tabela 5: dataset_finetune
-- Dados estruturados para o fine-tuning supervisionado dos modelos.
-- ---------------------------------------------------------------------
CREATE TABLE dataset_finetune (
    id_ft UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_agente UUID NOT NULL REFERENCES agentes(id_agente) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    completado TEXT NOT NULL, -- A resposta ideal (completion)
    tipo_origem TEXT, -- Ex: 'manual', 'interacao_curada'
    origem TEXT, -- Ex: id_interacao de onde veio
    anotado_por TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE dataset_finetune IS 'Armazena pares de prompt/completion para o fine-tuning dos modelos de linguagem.';
CREATE INDEX idx_ft_agente ON dataset_finetune(id_agente);

-- ---------------------------------------------------------------------
-- Tabela 6: configuracoes_avancadas
-- Tabela chave-valor para configurações extras e flexíveis por agente.
-- ---------------------------------------------------------------------
CREATE TABLE configuracoes_avancadas (
    id_config UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_agente UUID NOT NULL REFERENCES agentes(id_agente) ON DELETE CASCADE,
    chave TEXT NOT NULL,
    valor JSONB,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (id_agente, chave)
);

COMMENT ON TABLE configuracoes_avancadas IS 'Permite configurações adicionais e flexíveis sem alterar a tabela principal de agentes.';
CREATE INDEX idx_conf_agente ON configuracoes_avancadas(id_agente);

-- ---------------------------------------------------------------------
-- Tabela 7: logs_autoRAG
-- Logs específicos para avaliar e melhorar o processo de RAG.
-- ---------------------------------------------------------------------
CREATE TABLE logs_autoRAG (
    id_log UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_agente UUID NOT NULL REFERENCES agentes(id_agente) ON DELETE CASCADE,
    entrada TEXT NOT NULL,
    contexto_rag TEXT,
    resposta_gerada TEXT,
    nota_feedback NUMERIC(3, 2), -- Nota de 0 a 1
    tipo_feedback TEXT, -- 'auto', 'humano'
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE logs_autoRAG IS 'Registra dados detalhados do pipeline RAG para permitir a avaliação e melhoria contínua (AutoRAG).';
CREATE INDEX idx_logs_agente ON logs_autoRAG(id_agente); 