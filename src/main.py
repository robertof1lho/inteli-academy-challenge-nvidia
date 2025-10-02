import json
import os
import traceback
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def safe_parse_output(output):
    """Converte a saída do CrewOutput/TaskOutput em dict Python válido"""
    print(f"🔍 Debug - Tipo do output: {type(output)}")
    
    if hasattr(output, "pydantic") and output.pydantic:
        print(f"🔍 Debug - Usando pydantic")
        return output.pydantic.dict() if hasattr(output.pydantic, "dict") else output.pydantic

    if hasattr(output, "json_dict"):
        print(f"🔍 Debug - Usando json_dict")
        if isinstance(output.json_dict, str):
            try:
                return json.loads(output.json_dict)
            except json.JSONDecodeError:
                return {}
        if isinstance(output.json_dict, dict):
            return output.json_dict

    if isinstance(output, str):
        print(f"🔍 Debug - Parsing string")
        try:
            return json.loads(output)
        except:
            return {}
    if isinstance(output, dict):
        print(f"🔍 Debug - Usando dict direto")
        return output

    print(f"🔍 Debug - Retornando dict vazio")
    return {}

def validate_startup_data(startups):
    """Valida se os dados das startups não são alucinações"""
    fake_indicators = [
        # Nomes de empresas falsas comuns
        "startup alpha", "startup beta", "company alpha", "company beta",
        "startup a", "startup b", "company a", "company b", 
        "example corp", "test company", "demo startup", "sample company",
        "fictional corp", "placeholder inc", "template ltd",
        "empresa alfa", "empresa beta", "startup exemplo", "companhia teste",
        
        # Websites falsos comuns  
        "example.com", "test.com", "alpha.startup", "beta.startup",
        "demo.com", "sample.com", "placeholder.com", "template.com",
        "fictional.com", "fake.com", "exemplo.com", "teste.com"
    ]
    
    validated_startups = []
    rejected_count = 0
    
    for startup in startups:
        name = startup.get("name", "").lower()
        website = startup.get("website", "").lower() if startup.get("website") else ""
        description = startup.get("description", "").lower() if startup.get("description") else ""
        
        # Verifica se é dados falsos
        is_fake_name = any(fake in name for fake in fake_indicators)
        is_fake_website = any(fake in website for fake in fake_indicators)
        is_fake_description = any(fake in description for fake in fake_indicators)
        
        # Verifica se o nome é muito genérico
        generic_patterns = ["startup", "company", "corp", "inc", "ltd", "empresa"] 
        is_too_generic = len(name.split()) <= 2 and any(pattern in name for pattern in generic_patterns)
        
        # Verifica se tem informação suficiente
        has_meaningful_info = (
            startup.get("name") and 
            len(startup.get("name", "")) > 2 and
            (startup.get("website") or startup.get("description"))
        )
        
        # Verifica se o nome não é muito curto ou muito longo
        name_length_ok = len(startup.get("name", "")) >= 2 and len(startup.get("name", "")) <= 100
        
        if (not (is_fake_name or is_fake_website or is_fake_description or is_too_generic) 
            and has_meaningful_info and name_length_ok):
            validated_startups.append(startup)
            print(f"✅ Startup válida: {startup.get('name')} - {startup.get('description', 'N/A')[:50]}...")
        else:
            rejected_count += 1
            reason = "dados falsos" if (is_fake_name or is_fake_website or is_fake_description) else \
                    "muito genérico" if is_too_generic else \
                    "informação insuficiente" if not has_meaningful_info else \
                    "nome inválido"
            print(f"❌ Rejeitando startup suspeita: {startup.get('name')} (motivo: {reason})")
    
    print(f"📊 Validação: {len(validated_startups)} aprovadas, {rejected_count} rejeitadas")
    return validated_startups

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
        from StartupCrew.crew import StartupCrew
        print("✅ StartupCrew importado")
    except ImportError as e:
        print(f"❌ Erro ao importar StartupCrew: {e}")
        exit(1)
        
    try:
        from SheetsCrew.crew import SheetsCrew
        print("✅ SheetsCrew importado")
    except ImportError as e:
        print(f"❌ Erro ao importar SheetsCrew: {e}")
        exit(1)

    # ID e aba da planilha
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
                self.startup_crew = StartupCrew().crew()
                print("✅ StartupCrew inicializado")
            except Exception as e:
                print(f"❌ Erro ao inicializar StartupCrew: {e}")
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
            
            try:
                print("⏳ Executando InvestorCrew...")
                inputs = {"thesis": thesis}
                
                investors_output = self.investor_crew.kickoff(inputs=inputs)
                print(f"✅ InvestorCrew concluído!")
                
                investors_data = safe_parse_output(investors_output)
                investors = investors_data.get("investors", [])
                print(f"📊 Encontrados {len(investors)} investidores")

                # Debug - mostrar investidores encontrados
                for inv in investors:
                    inv_name = inv.get("name") if isinstance(inv, dict) else getattr(inv, "name", None)
                    inv_portfolio = inv.get("portfolio_url") if isinstance(inv, dict) else getattr(inv, "portfolio_url", None)
                    print(f"  📋 {inv_name}: {inv_portfolio}")

                # Salva investidores na aba "Investors"
                if investors:
                    print("💾 Salvando investidores...")
                    self.sheets.save_investors(investors, worksheet_name="Investors")
                    print("✅ Investidores salvos!")
                else:
                    print("⚠️ Nenhum investidor encontrado!")
                    return

            except Exception as e:
                print(f"❌ Erro no InvestorCrew: {e}")
                traceback.print_exc()
                return

            # Busca nos portfolios das startups
            print("\n🔄 Iniciando busca nos portfolios...")
            all_startups = []
            successful_extractions = 0
            failed_extractions = 0

            for i, inv in enumerate(investors, 1):
                inv_name = inv.get("name") if isinstance(inv, dict) else getattr(inv, "name", None)
                inv_portfolio = inv.get("portfolio_url") if isinstance(inv, dict) else getattr(inv, "portfolio_url", None)

                print(f"\n📈 [{i}/{len(investors)}] Processando: {inv_name}")
                print(f"🔗 Portfolio URL: {inv_portfolio}")

                if inv_portfolio and inv_portfolio.lower() not in ['null', 'none', '']:
                    try:
                        print("⏳ Executando StartupCrew...")
                        startups_output = self.startup_crew.kickoff(inputs={"portfolio_url": inv_portfolio})
                        
                        startups_data = safe_parse_output(startups_output)
                        startups = startups_data.get("startups", [])
                        
                        print(f"📊 Encontradas {len(startups)} startups brutas de {inv_name}")

                        # VALIDAÇÃO ANTI-ALUCINAÇÃO MELHORADA
                        if startups:
                            validated_startups = validate_startup_data(startups)
                            
                            if validated_startups:
                                # Adiciona o nome do VC a cada startup
                                for startup in validated_startups:
                                    if not startup.get("investors"):
                                        startup["investors"] = [inv_name]
                                    startup["vc_name"] = inv_name
                                
                                print(f"💾 Salvando {len(validated_startups)} startups de {inv_name}...")
                                self.sheets.save_startups(validated_startups, vc_name=inv_name, worksheet_name="Startups")
                                all_startups.extend(validated_startups)
                                successful_extractions += 1
                                print(f"✅ Startups de {inv_name} salvas!")
                            else:
                                print(f"⚠️ Nenhuma startup válida após validação para {inv_name}")
                                failed_extractions += 1
                        else:
                            print(f"⚠️ Nenhuma startup encontrada para {inv_name}")
                            failed_extractions += 1
                            
                    except Exception as e:
                        print(f"❌ Erro ao processar {inv_name}: {e}")
                        print(f"🔍 Debug - Detalhes do erro: {str(e)}")
                        failed_extractions += 1
                        # Continua com o próximo investidor em caso de erro
                        continue
                else:
                    print(f"⚠️ Sem URL de portfolio válida para {inv_name}")
                    failed_extractions += 1

            print(f"\n🎉 Pipeline concluído!")
            print(f"📊 Total de investidores processados: {len(investors)}")
            print(f"📊 Extrações bem-sucedidas: {successful_extractions}")
            print(f"📊 Extrações falharam: {failed_extractions}")
            print(f"📊 Total de startups válidas encontradas: {len(all_startups)}")
            print(f"💾 Dados salvos no Google Sheets: {SHEET_ID}")
            
            # Resumo das startups encontradas por VC
            if all_startups:
                print(f"\n📋 Resumo por VC:")
                vc_summary = {}
                for startup in all_startups:
                    vc_name = startup.get("vc_name", "Desconhecido")
                    if vc_name not in vc_summary:
                        vc_summary[vc_name] = 0
                    vc_summary[vc_name] += 1
                
                for vc, count in vc_summary.items():
                    print(f"  📌 {vc}: {count} startups")

    try:
        pipeline = ResearchPipeline()
        pipeline.run(thesis)
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()