from src.backend.agents.validator_agent import ValidationAgent

def test_validator_minimal_ok():
    v = ValidationAgent()
    candidate = {
      "startup":{"name":"Cromai","website":"https://cromai.com","hq_country":"Brazil",
                 "industry":"AgTech","year_founded":2017,"ai_tech_used":["CV","GenAI"],
                 "nvidia_stack_alignment":["CUDA","TensorRT"]},
      "funding":{"last_round":"Series A","last_round_date":"2024-06-15",
                 "last_round_amount_usd":5000000,"lead_investors":["Fund X"],"other_investors":[]},
      "leadership":{"technical_lead_name":"Jane Doe","title":"CTO","linkedin_url":"https://www.linkedin.com/in/jane"},
      "programs":{"is_inception_member":"unknown","evidence_url":None,"other_programs":[]},
      "sources":{"primary":"https://cromai.com","secondary":None}
    }
    out = v.validate(candidate, db_startups=[])
    assert out["action"] == "ADD"
    assert out["record"]["funding"]["last_round_date"] == "2024-06-15"
