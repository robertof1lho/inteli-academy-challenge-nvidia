from src.backend.agents.db_query_agent import DBQueryAgent

def test_db_query_agent():
    agent = DBQueryAgent()
    prompt = "Crie um INSERT SQL para adicionar a startup 'Startup X' no setor 'HealthTech'."
    result = agent.query(prompt)
    assert "INSERT" in result.upper()
    print("✅ DBQueryAgent gerou query:", result)
