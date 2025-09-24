from crewai import Agent
from openai import OpenAI
import os

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

class ReasoningAgent:
    def __init__(self, model_name="nvidia/nvidia-nemotron-nano-9b-v2"):
        self.agent = Agent(
            name="Reasoning Agent",
            role="Analista de Mercado",
            goal="Interpretar e estruturar dados coletados",
            backstory="Este agente usa o Nemotron Nano via API para análises complexas e reasoning estruturado."
        )
        self.model_name = model_name

    def analyze(self, context: str, question: str) -> str:
        """Usa Nemotron via API para raciocínio"""
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Você é um analista de dados de startups."},
                {"role": "user", "content": f"Contexto: {context}\nPergunta: {question}"}
            ],
            temperature=0.6,
            top_p=0.9,
            max_tokens=1024,
            extra_body={
                "min_thinking_tokens": 256,
                "max_thinking_tokens": 512
            }
        )
        # Pode vir reasoning separado
        reasoning = getattr(completion.choices[0].message, "reasoning_content", None)
        if reasoning:
            print("🧠 Raciocínio do modelo:", reasoning)

        return completion.choices[0].message.content
