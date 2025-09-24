# Script para atualização periódica do banco
import os, json, logging
from dotenv import load_dotenv
import psycopg
from typing import Dict, Any, List

from src.backend.agents.db_query_agent import DBQueryAgent

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

DB_URL = os.getenv("DATABASE_URL")

def _extract_sql_and_params(db_response_text: str) -> tuple[str, List[Any]]:
    """
    Your DB agent should return:
      1) a short summary line
      2) the SQL script with $1..$n params (BEGIN…COMMIT)
      3) the ordered parameter list (JSON or pretty-printed)
    Parse accordingly. For simplicity here, we expect a JSON block at the end:
      --- SQL ---
      --- PARAMS: [...]
    Adjust this parser to your agent’s exact format.
    """
    marker = "PARAMS:"
    if marker not in db_response_text:
        raise ValueError("DB agent did not return PARAMS marker")
    sql = db_response_text.split(marker)[0].strip()
    params_json = db_response_text.split(marker, 1)[1].strip()
    params = json.loads(params_json)
    return sql, params

def run_update(validated_path: str):
    if not os.path.exists(validated_path):
        raise FileNotFoundError(validated_path)

    with open(validated_path, "r", encoding="utf-8") as f:
        records: List[Dict[str, Any]] = json.load(f)

    db_agent = DBQueryAgent()
    success, failed = 0, 0

    with psycopg.connect(DB_URL, autocommit=False) as conn:
        for rec in records:
            prompt = (
                "mode: sql_batch\n"
                "task: generate a single transaction-safe SQL script (UPSERT) with numbered parameters.\n"
                "rules: use INSERT ... ON CONFLICT for startups (name,website), link funding per investor, "
                "upsert leadership (by startup_id,name,role), and persist raw JSON into raw_data.\n"
                f"payload:\n{json.dumps(rec, ensure_ascii=False)}"
            )
            resp_text = db_agent.query(prompt)
            sql, params = _extract_sql_and_params(resp_text)

            try:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                conn.commit()
                success += 1
            except Exception as e:
                logging.exception(f"Failed to upsert record: {e}")
                conn.rollback()
                failed += 1

    logging.info(f"DB update complete: {success} succeeded, {failed} failed")
    return {"ok": success, "failed": failed}

if __name__ == "__main__":
    run_update("validated_batch.json")
