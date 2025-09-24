from src.backend.agents.report_agent  import ReasoningAgent


def test_reasoning_agent():
    agent = ReasoningAgent()
    context = "Startup X levantou 5M USD em rodada série A com a Astella."
    result = agent.analyze(context, "Resuma em JSON com startup, rodada e investidor")
    assert isinstance(result, str)
    print("✅ ReasoningAgent retornou:", result)
