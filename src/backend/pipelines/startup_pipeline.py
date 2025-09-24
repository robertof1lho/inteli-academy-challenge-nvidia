from src.backend.agents.startup_agent import ResearchAgent
from src.backend.agents.db_query_agent import DBQueryAgent
from src.backend.agents.validator_agent import ValidationAgent

class StartupPipeline:
    def __init__(self):
        self.researcher = ResearchAgent()
        self.db_agent = DBQueryAgent()
        self.validator = ValidationAgent()

    def run(self, topic: str):
        
        print("Gerando query para salvar no banco...")
        query = self.db_agent.query(f"Returne the startups in the database with name and website only.")
        
        print(f"Buscando informações sobre: {topic}")
        search_results = self.researcher.search(topic, db_startups={query})


        print(f"Validação: {topic}")
        search_results = self.validator.validate(topic, db_startups={query})

        print("Gerando query para salvar no banco...")
        query = self.db_agent.query(f"Gere um INSERT para a tabela startups com: {search_results}")

        return {"web_search": search_results, "sql": query}
