# Script para exportação de relatórios
import os, csv, logging
from dotenv import load_dotenv
from supabase import create_client, Client  # supabase-py
from typing import List, Dict, Any

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def _sb() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def export_latest_rounds_csv(out_path: str = "latest_rounds.csv") -> str:
    sb = _sb()
    # Example: join-like behavior with two queries (simple and paginated)
    # 1) Fetch startups
    startups = sb.table("startups").select("id,name,website,country,sector").execute().data

    # 2) Fetch funding by startup (you can paginate with .range())
    funding = sb.table("funding_rounds").select("startup_id,amount,round_date,investor_name").execute().data

    # Index funding by startup_id
    by_sid: Dict[int, List[Dict[str, Any]]] = {}
    for r in funding:
        by_sid.setdefault(r["startup_id"], []).append(r)

    # Prepare flat rows (e.g., most recent round per startup)
    rows = []
    for s in startups:
        sid = s["id"]
        rounds = sorted(by_sid.get(sid, []), key=lambda x: x["round_date"] or "", reverse=True)
        top = rounds[0] if rounds else {"amount": None, "round_date": None, "investor_name": None}
        rows.append({
            "name": s["name"],
            "website": s["website"],
            "country": s.get("country"),
            "sector": s.get("sector"),
            "last_round_amount_usd": top["amount"],
            "last_round_date": top["round_date"],
            "last_round_lead_or_first_investor": top["investor_name"],
        })

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)

    logging.info(f"Exported {len(rows)} rows → {out_path}")
    return out_path

if __name__ == "__main__":
    export_latest_rounds_csv()
