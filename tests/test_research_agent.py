from src.backend.agents.startup_agent import ResearchAgent

def test_research_agent():
    agent = ResearchAgent()
    result = agent.search("10 Startups de IA no Brasil e link do site delas")
    assert result is not None
    print("✅ ResearchAgent retornou:", result)