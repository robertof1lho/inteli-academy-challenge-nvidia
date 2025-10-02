from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from crewai_tools import ScrapeWebsiteTool

@CrewBase
class ScrapingCrew():
    agents: list
    tasks: list

    @agent
    def portfolio_scraping_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['portfolio_scraping_agent'],
            tools=[ScrapeWebsiteTool()],
            verbose=True
        )

    @task
    def scrape_portfolio(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_portfolio'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.portfolio_scraping_agent()],
            tasks=[self.scrape_portfolio()],
            process=Process.sequential,
            verbose=True
        )

