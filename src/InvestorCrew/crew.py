import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Optional
from pydantic import BaseModel
from crewai_tools import SerperDevTool, ScrapeWebsiteTool


class Investor(BaseModel):
    name: str
    type: str
    website: str
    hq_country: str
    focus: str
    portfolio_url: Optional[str]

class InvestorList(BaseModel):
    investors: List[Investor]
    
    

@CrewBase
class InvestorCrew():
    agents: list
    tasks: list

    @agent
    def investor_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['investor_research_agent'],
            tools=[SerperDevTool()],
            verbose=True,
            allow_delegation=False,
            reasoning=True,
            max_reasoning_attempts=2,
            memory=True,
            llm='openai/nvidia/llama-3.3-nemotron-super-49b-v1'
        )

    @agent
    def investor_validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['investor_validation_agent'],
            tools=[ScrapeWebsiteTool()]
        )

    @agent
    def text2json_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['text2json_agent']
        )

    @task
    def investor_research(self) -> Task:
        return Task(
            config=self.tasks_config['discover_investors_raw'],
        )

    @task
    def validate_investor_websites(self) -> Task:
        return Task(
            config=self.tasks_config['validate_investors'],
        )

    @task
    def format_investors_json(self) -> Task:
        return Task(
            config=self.tasks_config['format_investors2json'],
            output_json=InvestorList,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.investor_research_agent(),
                self.investor_validation_agent(),
                self.text2json_agent()
            ],
            tasks=[
                self.investor_research(),
                self.validate_investor_websites(),
                self.format_investors_json()
            ],
            process=Process.sequential,
            verbose=True
        )
