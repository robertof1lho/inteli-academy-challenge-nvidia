import os
from crewai import Agent, Crew, Process, Task   
from crewai.project import CrewBase, agent, crew, task
        
from langchain_openai import ChatOpenAI
from composio import Composio
from composio_crewai import CrewAIProvider

openai_client = ChatOpenAI()
composio = Composio(provider=CrewAIProvider())
# Get All the tools
tools = composio.tools.get(user_id="default", toolkits=["GITHUB"])

        
@CrewBase
class SheetsCrew():
    agents: list
    tasks: list

    @agent
    def sheets_writer_agent(self) -> Agent:
        
        return Agent(
            config=self.agents_config['sheets_writer_agent'],
            tools=tools
        )

    @task
    def write_investors(self) -> Task:
        return Task(config=self.tasks_config['write_investors_to_spreadsheet'])

    @task
    def write_startups(self) -> Task:
        return Task(config=self.tasks_config['write_startups_to_spreadsheet'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.sheets_writer_agent()],
            tasks=[self.write_investors(), self.write_startups()],
            process=Process.sequential,
            verbose=True
        )
