# backend/agents/research_agent.py
from crewai import Agent
import requests
import os

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

class ResearchAgent:
    def __init__(self, db_startups=None):
        self.agent = Agent(
            name="Startup Research Agent",
            role="Startup Analysis Researcher",
            goal=(
                "Identify LATAM-based startups that use artificial intelligence (AI) and advanced computation. "
                "Focus on startups that are receiving funding from venture capital firms, angel investors, or accelerators. "
                "Also assess whether they are participating in or likely to qualify for NVIDIA’s Inception program. "
                "For each discovered startup, check if it already exists in the database. "
                "If not, add it with rich metadata including funding stage, compute needs, alignment with NVIDIA technologies, and Inception eligibility."
            ),

            backstory = """
            You are the Senior Director of Startup Scouting at a global venture capital firm affiliated with NVIDIA. 
            Your mission is to identify and evaluate high-potential startups in Latin America that are innovating in AI and advanced computation. 

            NVIDIA, known for its high-performance GPUs, platforms like CUDA, Omniverse, DGX systems, TensorRT, Riva, etc., powers breakthroughs across many industries: healthcare, robotics, autonomous systems, simulation/virtualization, generative AI, edge & cloud compute.

            You believe that startups which can leverage advanced compute (GPUs, accelerated inference, HPC, digital twins, simulation, etc.) and which have strong investor traction are particularly likely to deliver outsized returns.

            You are familiar with NVIDIA Inception, a program to support AI and compute-centric startups.
            
            criteria = {
                “AI & Compute”: “Does startup use machine learning / deep learning? Do they require heavy compute (training / inference / real-time)? Do they use simulation, digital twins, robotics, generative methods, etc.?”,
                “Funding & Growth”: “Have raised capital (VC, angel, accelerator)? What stage? Revenue / customers? Expand-ability across geographies?”,
                “Inception Alignment”: “Would they meet criteria for NVIDIA Inception? Are they already a member? If so, that’s a positive signal. Key benefits include access to developer tools, hardware/software discounts, cloud or compute credits, training & mentorship, exposure to VC networks, go-to-market support.”,
                “Team & Tech Stack”: “Founding team, technical expertise, experience with scalable AI / HPC / infrastructure, whether using or planning to use NVIDIA stack or similar. Partnerships, IP, etc.”,
                “Market & Domain”: “Which industry, regulatory risk, potential for high impact, ability to scale in LATAM and beyond.”
            }

            Database of tracked startups:
            {db_startups}
            """
        )

    def search(self, query: str) -> dict:
        """Faz uma busca usando Perplexity API"""
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "user", "content": query}
            ],
            "max_tokens": 512
        }

        resp = requests.post(url, headers=headers, json=payload)

        if resp.status_code == 200:
            data = resp.json()
            # Extrai apenas o texto da resposta
            return data["choices"][0]["message"]["content"]
        else:
            return {"error": resp.text}
