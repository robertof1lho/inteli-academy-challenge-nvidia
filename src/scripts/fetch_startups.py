# Script para coleta inicial de dados
import json, os, logging, time
from typing import List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from apscheduler.schedulers.blocking import BlockingScheduler

from src.backend.agents.startup_agent import ResearchAgent
from src.backend.agents.validator_agent import ValidationAgent

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---- HTTP retry policy: exponential backoff on transient failures
class TransientError(Exception): pass

def _is_transient(e: Exception) -> bool:
    return True  # tune as needed (HTTP 5xx, timeouts, rate limits)

@retry(reraise=True,
       retry=retry_if_exception_type(TransientError),
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1, min=1, max=16))
def _fetch_names(researcher: ResearchAgent, topic: str, limit: int = 10) -> List[str]:
    q = (f"List up to {limit} LATAM AI/accelerated-compute startups with recent funding. "
         f"Topic hint: {topic}. Return JSON with a 'names' list only.")
    resp = researcher.search(q)
    if not isinstance(resp, dict) or "names" not in resp:
        raise TransientError("Unexpected response for names")
    return resp["names"][:limit]

@retry(reraise=True,
       retry=retry_if_exception_type(TransientError),
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1, min=1, max=16))
def _fetch_candidate(researcher: ResearchAgent, name: str) -> Dict[str, Any]:
    q = ("Return canonical facts as JSON for startup '{name}': website, HQ country, industry, "
         "year founded, AI tech used, NVIDIA stack alignment (CUDA/TensorRT/Triton/DGX/Omniverse/"
         "Isaac/Riva/NeMo/NIM/AIE), last funding (round/date/amount/investors), "
         "technical leader (name/title/LinkedIn), plus primary and secondary sources.").format(name=name)
    resp = researcher.search(q)
    if not isinstance(resp, dict):
        raise TransientError("Unexpected candidate shape")
    return resp

def run_discovery(topic: str, db_snapshot: List[Dict[str, Any]] | None = None, out_path: str = "validated_batch.json"):
    researcher = ResearchAgent()
    validator  = ValidationAgent()

    logging.info(f"Discovering startups for topic: {topic}")
    names = _fetch_names(researcher, topic, limit=12)

    validated_records = []
    for name in names:
        logging.info(f"[{name}] collecting facts…")
        candidate = _fetch_candidate(researcher, name)

        logging.info(f"[{name}] validating…")
        val = validator.validate(candidate=candidate, db_startups=db_snapshot or [])
        if val.get("action") == "ADD":
            validated_records.append(val["record"])
        else:
            logging.info(f"[{name}] skipped ({val.get('action')})")

        time.sleep(0.3)  # polite pacing

    if not validated_records:
        logging.warning("No new records to save.")
        return None

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(validated_records, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved {len(validated_records)} validated records → {out_path}")
    return out_path

# ---- Optional scheduler (cron/interval). Use one process per service.
def schedule_job():
    sched = BlockingScheduler()
    # run every 6 hours
    sched.add_job(run_discovery, "interval", hours=6, kwargs={"topic": "LATAM GenAI + computer vision 2024-2025"})
    logging.info("Scheduler started (every 6h).")
    sched.start()

if __name__ == "__main__":
    # one-off:
    run_discovery(topic="Brazil & Mexico AI startups Series A 2024-2025")
    # or schedule_job()
