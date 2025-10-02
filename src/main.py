import json
import os
import traceback
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def safe_parse_output(output):
    """Converte a saída do CrewOutput/TaskOutput em dict Python válido"""
    print(f"🔍 Debug - Tipo do output: {type(output)}")
    print(f"🔍 Debug - Output raw: {output}")
    
    if hasattr(output, "pydantic") and output.pydantic:
        print(f"🔍 Debug - Usando pydantic: {output.pydantic}")
        return output.pydantic.dict() if hasattr(output.pydantic, "dict") else output.pydantic

    if hasattr(output, "json_dict"):
        print(f"🔍 Debug - Usando json_dict: {output.json_dict}")
        if isinstance(output.json_dict, str):
            try:
                return json.loads(output.json_dict)
            except json.JSONDecodeError:
                return {}
        if isinstance(output.json_dict, dict):
            return output.json_dict

    if isinstance(output, str):
        print(f"🔍 Debug - Parsing string: {output}")
        try:
            return json.loads(output)
        except:
            return {}
    if isinstance(output, dict):
        print(f"🔍 Debug - Usando dict direto: {output}")
        return output

    print(f"🔍 Debug - Retornando dict vazio")
    return {}

if __name__ == "__main__":
    # VERIFICAR CHAVES DA API
    print("🔑 Verificando chaves da API...")
    
    # Verifica todas as chaves importantes
    openai_key = os.getenv("OPENAI_API_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    print(f"✅ OPENAI_API_KEY: {'✓' if openai_key else '✗'}")
    print(f"✅ PERPLEXITY_API_KEY: {'✓' if perplexity_key else '✗'}")
    print(f"✅ GROQ_API_KEY: {'✓' if groq_key else '✗'}")
    
    if not any([openai_key, perplexity_key, groq_key]):
        print("❌ Nenhuma chave de API encontrada!")
        exit(1)

    thesis = "LATAM AI / accelerated-compute VCs, CVCs, Angels and their startup portfolios"

    # Importações corretas
    try:
        from InvestorCrew.crew import InvestorCrew
        print("✅ InvestorCrew importado")
    except ImportError as e:
        print(f"❌ Erro ao importar InvestorCrew: {e}")
        exit(1)
        
    try:
        from ScrapingCrew.crew import ScrapingCrew
        print("✅ ScrapingCrew importado")
    except ImportError as e:
        print(f"❌ Erro ao importar ScrapingCrew: {e}")
        exit(1)
        
    try:
        from SheetsCrew.crew import SheetsCrew
        print("✅ SheetsCrew importado")
    except ImportError as e:
        print(f"❌ Erro ao importar SheetsCrew: {e}")
        exit(1)

    # ADICIONE: ID e aba
    SHEET_ID = "1auRAUym5fJDgM16p2T5eCby4wflZatwLMK3NXAOGdCo"
    SHEET_TAB = "Funding Round"

    class ResearchPipeline:
        def __init__(self):
            print("🔧 Inicializando crews...")
            try:
                self.investor_crew = InvestorCrew().crew()
                print("✅ InvestorCrew inicializado")
            except Exception as e:
                print(f"❌ Erro ao inicializar InvestorCrew: {e}")
                raise
                
            try:
                self.scraping_crew = ScrapingCrew().crew()
                print("✅ ScrapingCrew inicializado")
            except Exception as e:
                print(f"❌ Erro ao inicializar ScrapingCrew: {e}")
                raise
                
            try:
                self.sheets = SheetsCrew(spreadsheet_id=SHEET_ID, worksheet_name=SHEET_TAB)
                print("✅ SheetsCrew inicializado")
            except Exception as e:
                print(f"❌ Erro ao inicializar SheetsCrew: {e}")
                raise
                
            print("✅ Todos os crews inicializados!")

        def run(self, thesis: str):
            print(f"🚀 Rodando pipeline para tese: {thesis}")
            print(f"📝 Input thesis: '{thesis}'")
            
            try:
                print("⏳ Executando InvestorCrew...")
                # Adiciona debug do input
                inputs = {"thesis": thesis}
                print(f"📤 Enviando inputs: {inputs}")
                
                investors_output = self.investor_crew.kickoff(inputs=inputs)
                print(f"✅ InvestorCrew concluído!")
                
                investors_data = safe_parse_output(investors_output)
                investors = investors_data.get("investors", [])
                print(f"📊 Encontrados {len(investors)} investidores")

                # Salva investidores na aba "Investors"
                if investors:
                    print("💾 Salvando investidores...")
                    self.sheets.save_investors(investors, worksheet_name="Investors")
                    print("✅ Investidores salvos!")
                else:
                    print("⚠️ Nenhum investidor encontrado!")

            except Exception as e:
                print(f"❌ Erro no InvestorCrew: {e}")
                print(f"❌ Tipo do erro: {type(e)}")
                traceback.print_exc()
                return

            # Para debugar, vamos parar aqui por enquanto
            print("🛑 Parando aqui para debug. Comente esta linha para continuar.")
            return

            all_startups = []

            for inv in investors:
                inv_name = inv.get("name") if isinstance(inv, dict) else getattr(inv, "name", None)
                inv_portfolio = inv.get("portfolio_url") if isinstance(inv, dict) else getattr(inv, "portfolio_url", None)

                print(f"Scraping portfolio: {inv_name}")
                print(f"Portfolio URL: {inv_portfolio}")

                if inv_portfolio:  # Só faz scraping se tiver URL
                    startups_output = self.scraping_crew.kickoff(inputs={"portfolio_url": inv_portfolio})
                    startups_data = safe_parse_output(startups_output)
                    startups = startups_data.get("startups", [])

                    # Salva startups na aba "Startups" com o nome do VC
                    self.sheets.save_startups(startups, vc_name=inv_name, worksheet_name="Startups")

                    all_startups.extend(startups)

            print(f"💾 Processo concluído! Dados salvos no Google Sheets.")

    try:
        pipeline = ResearchPipeline()
        pipeline.run(thesis)
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()