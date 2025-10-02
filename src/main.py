if __name__ == "__main__":
    thesis = "LATAM AI / accelerated-compute VCs, CVCs, Angels and their startup portfolios"
    
    from InvestorCrew.crew import InvestorCrew
    from ScrapingCrew.crew import ScrapingCrew
    from SheetsCrew.crew import SheetsCrew


    class ResearchPipeline:
        def __init__(self):
            self.investor_crew = InvestorCrew().crew()
            self.scraping_crew = ScrapingCrew().crew()
            self.sheets_crew = SheetsCrew().crew()

        def run(self, thesis: str):
            print(f"🚀 Rodando pipeline para tese: {thesis}")
            investors_output = self.investor_crew.kickoff(inputs={"thesis": thesis})
            investors = investors_output["investors"]

            all_startups = []

            for inv in investors:
                print(f"Scraping portfolio: {inv['name']}")
                startups = self.scraping_crew.kickoff(inputs={"portfolio_url": inv["portfolio_url"]})
                for startup in startups:
                    startup["vc_name"] = inv["name"]
                all_startups.extend(startups)

            print(f"📊 Salvando tudo em planilha...")
            self.sheets_crew.kickoff(inputs={
                "investors": investors,
                "startups": all_startups
            })



    pipeline = ResearchPipeline()
    pipeline.run(thesis)








