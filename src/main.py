import json

def safe_parse_output(output):
    """Converte a saída do CrewOutput/TaskOutput em dict Python válido"""
    if hasattr(output, "pydantic") and output.pydantic:
        return output.pydantic.dict() if hasattr(output.pydantic, "dict") else output.pydantic

    if hasattr(output, "json_dict"):
        if isinstance(output.json_dict, str):
            try:
                return json.loads(output.json_dict)
            except json.JSONDecodeError:
                return {}
        if isinstance(output.json_dict, dict):
            return output.json_dict

    if isinstance(output, str):
        try:
            return json.loads(output)
        except:
            return {}
    if isinstance(output, dict):
        return output

    return {}


if __name__ == "__main__":
    thesis = "LATAM AI / accelerated-compute VCs, CVCs, Angels and their startup portfolios"

    from InvestorCrew.crew import InvestorCrew
    from ScrapingCrew.crew import ScrapingCrew
    # from DBcrew.crew import DBCrew
    from SheetsCrew.crew import SheetsCrew

    class ResearchPipeline:
        def __init__(self):
            self.investor_crew = InvestorCrew().crew()
            self.scraping_crew = ScrapingCrew().crew()
            # self.db_crew = DBCrew().crew()
            self.sheets_crew = SheetsCrew().crew()

        def run(self, thesis: str):
            print(f"🚀 Rodando pipeline para tese: {thesis}")
            investors_output = self.investor_crew.kickoff(inputs={"thesis": thesis})
            investors_data = safe_parse_output(investors_output)
            investors = investors_data.get("investors", [])

            all_startups = []

            for inv in investors:
                inv_name = inv.get("name") if isinstance(inv, dict) else getattr(inv, "name", None)
                inv_portfolio = inv.get("portfolio_url") if isinstance(inv, dict) else getattr(inv, "portfolio_url", None)

                print(f"Scraping portfolio: {inv_name}")
                print(f"Portfolio URL: {inv_portfolio}")

                startups_output = self.scraping_crew.kickoff(inputs={"portfolio_url": inv_portfolio})
                startups_data = safe_parse_output(startups_output)
                startups = startups_data.get("startups", [])

                for startup in startups:
                    # normaliza dict ou objeto pydantic
                    if not isinstance(startup, dict) and hasattr(startup, "dict"):
                        startup = startup.dict()

                    if isinstance(startup, dict):
                        startup["investors"] = [inv_name]
                    else:
                        startup.investors = [inv_name]

                    all_startups.append(startup)

                print(f"💾 Salvando no Google Sheets...")
                self.sheets_crew.save_investors(investors)
                self.sheets_crew.save_startups(all_startups)

    pipeline = ResearchPipeline()
    pipeline.run(thesis)
