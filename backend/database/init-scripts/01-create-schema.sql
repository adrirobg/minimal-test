-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create database user if not exists (for development)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'kairos_user') THEN
        CREATE ROLE kairos_user WITH LOGIN PASSWORD 'kairos_password';
    END IF;
END
$$;

-- Grant permissions
GRANT CONNECT ON DATABASE kairos_bcp_dev TO kairos_user;
GRANT USAGE ON SCHEMA public TO kairos_user;
GRANT CREATE ON SCHEMA public TO kairos_user;

-- Create indexes for better performance (these will be created by Alembic too)
-- Vector similarity index will be created when the embeddings column is added