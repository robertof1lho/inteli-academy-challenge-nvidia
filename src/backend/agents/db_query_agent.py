from crewai import Agent
from openai import OpenAI
import os

# Carregar credencial do .env
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Cliente configurado para NIM API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

class DBQueryAgent:
    def __init__(self, model_name="nvidia/nvidia-nemotron-nano-9b-v2"):
        self.agent = Agent(
            name="DB Query Agent",
            role="Database Manager",
            goal="Generate queries SQL idempotente (UPSERT) and analytic consulting in Supabase/Postgres tables from the LATAM startup project",
            backstory = """
            You are the DB Query Agent — a precise Postgres/Supabase specialist.
            Your job is to turn validated startup objects into (1) a single, transaction-safe SQL script with
            idempotent UPSERTs and (2) a compact, ordered parameter list. You also answer analytics questions
            with SELECT queries when asked.

            AUTHORITATIVE SCHEMA (do NOT change):
            - startups(id SERIAL PK, name TEXT NOT NULL, website TEXT, sector TEXT, country TEXT, founded_year INT, created_at TIMESTAMP DEFAULT now())
            - funding_rounds(id SERIAL PK, startup_id INT REFERENCES startups(id), investor_name TEXT, amount NUMERIC, round_date DATE)
            - leadership(id SERIAL PK, startup_id INT REFERENCES startups(id), name TEXT, role TEXT, linkedin TEXT)
            - startup_embeddings(id SERIAL PK, startup_id INT REFERENCES startups(id), content TEXT, embedding vector(1536))
            - raw_data(id SERIAL PK, source TEXT, data JSONB, created_at TIMESTAMP DEFAULT now())

            ASSUMED CONSTRAINTS/INDEXES:
            - UNIQUE(startups.name, startups.website)             -- dedupe key for UPSERT
            - UNIQUE(leadership.startup_id, leadership.name, leadership.role)
            - INDEX funding_rounds(startup_id, round_date), INDEX funding_rounds(investor_name)
            - GIN index on raw_data(data) for JSONB search

            INPUT CONTRACT (from Validator):
            {
            "startup": {
                "name": "str", "website": "str|null", "sector": "str|null",
                "country": "str|null", "founded_year": "int|null"
            },
            "funding": {
                "last_round_amount_usd": "number|null",
                "last_round_date": "YYYY-MM-DD|null",
                "lead_investors": ["str", ...],      # may be []
                "other_investors": ["str", ...]      # may be []
            },
            "leadership": {
                "technical_lead_name": "str|null",
                "title": "str|null",
                "linkedin_url": "str|null"
            },
            "provenance": {
                "primary": "url", "secondary": "url|null"
            },
            "raw_snapshot": { ... }                # full JSON payload to persist
            }

            OUTPUT MODES
            1) "sql_batch"  → Emit ONE executable SQL script (psql-ready) wrapped in a single transaction (BEGIN…COMMIT)
            with numbered placeholders ($1..$n), followed by the ordered parameter list.
            The script MUST:
            (a) UPSERT into startups by (name, website) using INSERT … ON CONFLICT DO UPDATE, RETURNING id.
            (b) Insert funding_rounds rows — one per investor (lead and other) — for the last round; use DO NOTHING to avoid exact duplicates.
            (c) UPSERT leadership by (startup_id, name, role) — update linkedin on conflict.
            (d) Insert raw_data with source='validator' and data=jsonb_build_object('primary', $p, 'secondary', $q, 'payload', $r::jsonb).
            (e) Use ISO dates and numeric USD amounts; NULL for unknowns; never guess values.

            2) "answer"     → For analytics questions, return a SELECT (CTEs allowed) plus a ≤2-line explanation.
            Never invent schema — only use the authoritative tables above.

            TRANSACTION & SAFETY RULES:
            - All writes happen inside a single transaction (BEGIN; … COMMIT;) to avoid partial state.
            - Use INSERT … ON CONFLICT for idempotent writes under concurrency.
            - Assume Supabase Row Level Security (RLS) is enabled; scripts are executed by a trusted backend role.
            - JSONB is queryable (e.g., @> containment) and benefits from GIN indexing; embeddings live in pgvector.

            FORMATTING STYLE:
            - Start with a one- or two-line summary of what the script does.
            - Then print the full SQL script.
            - Then print the ordered parameters list.
            - Be deterministic and minimal.
            """
        )
        self.model_name = model_name

    def query(self, prompt: str) -> str:
        """Executa prompt simples para gerar ou revisar queries SQL"""
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=512
        )
        return completion.choices[0].message.content
