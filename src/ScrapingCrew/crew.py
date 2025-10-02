from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
# from crewai_tools import ScrapeWebsiteTool
from typing import List, Optional
from pydantic import BaseModel

llm = LLM(
    model="perplexity/sonar",
    base_url="https://api.perplexity.ai/",
    api_key=os.getenv("PERPLEXITY_API_KEY")
)

class LeadershipPerson(BaseModel):
    role: str
    name: str
    linkedin: Optional[str] = None

class StartupCandidate(BaseModel):
    name: str
    website: Optional[str] = None
    sector: Optional[str] = None
    year: Optional[int] = None
    tech: Optional[List[str]] = None
    funding: Optional[str] = None
    investors: Optional[List[str]] = None
    leadership: Optional[List[dict]] = None

class StartupList(BaseModel):
    startups: List[StartupCandidate]

@CrewBase
class ScrapingCrew():
    agents: list
    tasks: list

    @agent
    def portfolio_scraping_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['portfolio_scraping_agent'],
            # tools=[ScrapeWebsiteTool()],
            verbose=True,
            llm=llm
        )
        
    @agent
    def text2json_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['text2json_agent']
        )
        
    @task
    def scrape_portfolio(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_portfolio'],
        )
    
    @task
    def format_startups_json(self) -> Task:
        return Task(
            config=self.tasks_config['format_startup2json'],
            output_pydantic=StartupList,  # Mudança: usar output_pydantic em vez de output_json
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.portfolio_scraping_agent(), self.text2json_agent()],  # Adicione o segundo agente
            tasks=[self.scrape_portfolio(), self.format_startups_json()],
            process=Process.sequential,
            verbose=True
        )