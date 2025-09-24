# Pesquisa e compreensão de mercado
from crewai import Agent
import requests
import os

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

class ResearchAgent:
    def __init__(self):
        self.agent = Agent(
            name="Research Agent",
            role="Pesquisador",
            goal="Buscar informações sobre startups na internet",
            backstory="Este agente utiliza Perplexity para pesquisar startups, VCs e tendências de mercado."
        )

    def search(self, query: str) -> dict:
        """Faz uma busca usando Perplexity API"""
        headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}"}
        url = "https://api.perplexity.ai/search"
        payload = {"q": query, "num_results": 5}
        resp = requests.post(url, headers=headers, json=payload)

        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": resp.text}
