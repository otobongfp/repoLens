-- Initialize PostgreSQL with vector extension
-- This script runs when the PostgreSQL container starts for the first time

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a sample table for testing vector operations
CREATE TABLE IF NOT EXISTS code_embeddings (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    function_name TEXT,
    embedding VECTOR(1536), -- OpenAI embedding dimension
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on the vector column for efficient similarity search
CREATE INDEX IF NOT EXISTS code_embeddings_embedding_idx 
ON code_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Create a table for project metadata
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_id UUID UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    source_config JSONB,
    storage_config JSONB,
    status TEXT DEFAULT 'created',
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP,
    analysis_count INTEGER DEFAULT 0,
    file_count INTEGER,
    size_bytes BIGINT
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS projects_project_id_idx ON projects(project_id);
CREATE INDEX IF NOT EXISTS projects_tenant_id_idx ON projects(tenant_id);
CREATE INDEX IF NOT EXISTS projects_status_idx ON projects(status);

-- Create a table for analysis results
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_id UUID UNIQUE NOT NULL,
    project_id UUID NOT NULL,
    analysis_type TEXT NOT NULL,
    status TEXT DEFAULT 'started',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    progress JSONB,
    results JSONB,
    error_message TEXT
);

-- Create indexes for analysis results
CREATE INDEX IF NOT EXISTS analysis_results_project_id_idx ON analysis_results(project_id);
CREATE INDEX IF NOT EXISTS analysis_results_status_idx ON analysis_results(status);
CREATE INDEX IF NOT EXISTS analysis_results_started_at_idx ON analysis_results(started_at);

-- Grant permissions to the repolens user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO repolens;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO repolens;
