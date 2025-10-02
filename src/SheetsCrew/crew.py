import os
from crewai import Agent, Crew, Process, Task   
from crewai.project import CrewBase, agent, crew, task


import gspread
from oauth2client.service_account import ServiceAccountCredentials

base_dir = os.path.dirname(__file__)  # pega a pasta do crew.py
cred_path = os.path.join(base_dir, "config", "credentials.json")
        
@CrewBase
class SheetsCrew():
    def __init__(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open("inteli academy").worksheet("Investors")

    def save_investors(self, investors):
        for inv in investors:
            row = [inv.get("name"), inv.get("website"), inv.get("type"), inv.get("focus")]
            self.sheet.append_row(row)

    def save_startups(self, startups):
        ws = self.client.open("inteli academy").worksheet("Startups")
        for st in startups:
            row = [st.get("name"), st.get("website"), st.get("sector"), st.get("founded_year")]
            ws.append_row(row)






















    # agents: list
    # tasks: list

    # @agent
    # def sheets_writer_agent(self) -> Agent:
        
    #     return Agent(
    #         config=self.agents_config['sheets_writer_agent'],
    #         tools=tools
    #     )

    # @task
    # def write_investors(self) -> Task:
    #     return Task(config=self.tasks_config['write_investors_to_spreadsheet'])

    # @task
    # def write_startups(self) -> Task:
    #     return Task(config=self.tasks_config['write_startups_to_spreadsheet'])

    # @crew
    # def crew(self) -> Crew:
    #     return Crew(
    #         agents=[self.sheets_writer_agent()],
    #         tasks=[self.write_investors(), self.write_startups()],
    #         process=Process.sequential,
    #         verbose=True
    #     )
