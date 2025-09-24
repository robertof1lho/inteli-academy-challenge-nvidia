-- ========================
-- EXTENSÕES NECESSÁRIAS
-- ========================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;

-- ========================
-- TABELAS RELACIONAIS
-- ========================
-- Startups
CREATE TABLE startups (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  website TEXT,
  sector TEXT,
  country TEXT,
  founded_year INT,
  created_at TIMESTAMP DEFAULT now()
);

-- Rodadas de Investimento
CREATE TABLE funding_rounds (
  id SERIAL PRIMARY KEY,
  startup_id INT REFERENCES startups(id) ON DELETE CASCADE,
  investor_name TEXT,
  amount NUMERIC,
  round_date DATE
);

-- Lideranças
CREATE TABLE leadership (
  id SERIAL PRIMARY KEY,
  startup_id INT REFERENCES startups(id) ON DELETE CASCADE,
  name TEXT,
  role TEXT,
  linkedin TEXT
);

-- ========================
-- EMBEDDINGS
-- ========================
CREATE TABLE startup_embeddings (
  id SERIAL PRIMARY KEY,
  startup_id INT REFERENCES startups(id) ON DELETE CASCADE,
  content TEXT,          -- Texto bruto (descrição, artigo, perfil)
  embedding vector(1536) -- Exemplo: OpenAI ou Nemotron embeddings
);

-- ========================
-- RAW DATA (pré-validação)
-- ========================
CREATE TABLE raw_data (
  id SERIAL PRIMARY KEY,
  source TEXT,           -- ex: "LinkedIn", "Crunchbase"
  data JSONB,            -- Dump bruto da coleta
  created_at TIMESTAMP DEFAULT now()
);
