# baseline.py
import os
import json
from pathlib import Path
from google import genai
from llm_utils import safe_generate_json
from tracer import AgentObservability
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_baseline_on_case(case_dir: Path) -> dict:
    obs = AgentObservability(case_id=case_dir.name)

    with open(case_dir / "openapi.yaml", "r", encoding="utf-8") as f:
        spec_text = f.read()
    with open(case_dir / "traffic.jsonl", "r", encoding="utf-8") as f:
        logs_text = f.read()

    obs.record_step("INITIALIZE", {"case_id": case_dir.name, "spec": spec_text})

    prompt = f"""You are an API validator. Inspect this OpenAPI spec and traffic logs.
OpenAPI Spec:
{spec_text}

Traffic Logs:
{logs_text}

Return JSON ONLY:
{{
  "drift_detected": true/false,
  "drift_type": "SHADOW_HEADER" | "TYPE_WIDENING" | "NULLABILITY_DRIFT" | "ENUM_DRIFT" | "STATUS_CODE_DRIFT" | "ERROR_SCHEMA_DRIFT" | "NESTED_SHADOW_FIELD" | "POLYMORPHIC_SHADOW_FIELD" | "NONE",
  "field": "name_of_field_or_none"
}}"""

    obs.record_step("PROMPT", {"prompt": prompt})

    result = safe_generate_json(
        client,
        model="models/gemini-3.1-flash-lite",
        contents=prompt,
        config={"response_mime_type": "application/json", "temperature": 0.0},
        max_retries=4,
    )
    obs.record_step("LLM_RESPONSE", {"result": result})
    obs.record_step("FINAL_VERDICT", result)
    obs.export_trajectory()
    return result