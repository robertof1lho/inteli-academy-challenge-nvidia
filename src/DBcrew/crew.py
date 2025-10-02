import os
from crewai import Agent, Crew, Process, Task   
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import NL2SQLTool

DATABASE_URI = os.getenv("DATABASE_URI")

nl2sql = NL2SQLTool(db_uri=DATABASE_URI)

        
@CrewBase
class DBCrew():
    agents: list
    tasks: list

    @agent
    def db_agent(self) -> Agent:
        
        return Agent(
            config=self.agents_config['db_agent'],
            tools=[nl2sql]
        )

    @task
    def save_to_database(self) -> Task:
        return Task(config=self.tasks_config['save_to_db'])


    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.db_agent()],
            tasks=[self.write_investors(), self.save_to_database()],
            process=Process.sequential,
            verbose=True
        )
