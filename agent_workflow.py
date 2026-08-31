# agent_workflow.py
import os
import json
import yaml
from pathlib import Path
from google import genai
from dotenv import load_dotenv
from tracer import AgentObservability
from llm_utils import safe_generate_json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_log_clusters(case_id: str) -> dict:
    """Deterministic tool: clusters payloads and removes 400 Bad Request spam."""
    logs_file = Path("data") / case_id / "traffic.jsonl"
    with open(logs_file, "r", encoding="utf-8") as f:
        logs = [json.loads(line) for line in f]
    
    # 1. Filter out 400 Bad Requests (Spam filter for Case 9)
    valid_logs = [l for l in logs if l.get("status") != 400]
    if not valid_logs:
        return {"status": "ALL_SPAM_400", "is_spam": True}
    
    sample = valid_logs[0]
    headers = list(sample.get("headers", {}).keys()) if sample.get("headers") else []
    # Collect body field key sets across valid logs to detect polymorphic patterns
    body_field_sets = []
    for l in valid_logs:
        body = l.get("body") or l.get("response_body") or {}
        if isinstance(body, dict):
            body_field_sets.append(set(body.keys()))
        else:
            body_field_sets.append(set())

    # Compute union and intersection of observed keys
    if body_field_sets:
        union_keys = set.union(*body_field_sets)
        intersection_keys = set.intersection(*body_field_sets)
    else:
        union_keys = set()
        intersection_keys = set()

    variable_keys = list(sorted(union_keys - intersection_keys))
    polymorphic_candidate = len(variable_keys) >= 2

    # Provide a compact representative of body fields from the first sample
    body_data = sample.get("body") or sample.get("response_body") or {}

    return {
        "is_spam": False,
        "status_code": sample.get("status"),
        "headers": headers,
        "body_fields": body_data,
        "observed_union_fields": list(sorted(union_keys)),
        "observed_common_fields": list(sorted(intersection_keys)),
        "variable_fields": variable_keys,
        "polymorphic_candidate": polymorphic_candidate,
    }

def run_agent_on_case(case_dir: Path) -> dict:
    case_id = case_dir.name
    obs = AgentObservability(case_id=case_id)
    
    with open(case_dir / "openapi.yaml", "r", encoding="utf-8") as f:
        spec_dict = yaml.safe_load(f)

    obs.record_step("INITIALIZE", {"case_id": case_id, "spec": spec_dict})
    
    # 1. Deterministic Tool Execution
    obs.record_step("TOOL_CALL", {"tool": "extract_log_clusters", "args": {"case_id": case_id}})
    cluster_res = extract_log_clusters(case_id)
    obs.record_step("TOOL_RESPONSE", {"result": cluster_res})

    # Case 9 Guard: If all traffic was 400 Bad Requests, it is client spam, not spec drift
    if cluster_res.get("is_spam"):
        result = {"drift_detected": False, "drift_type": "NONE", "field": "none"}
        obs.record_step("FINAL_VERDICT", result)
        obs.export_trajectory()
        return result

    # Quick heuristic: compare observed fields to spec properties to detect multi-field shadowing
    def collect_spec_properties(d: dict) -> set:
        props = set()
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "properties" and isinstance(v, dict):
                    props.update(v.keys())
                else:
                    props.update(collect_spec_properties(v))
        elif isinstance(d, list):
            for item in d:
                props.update(collect_spec_properties(item))
        return props

    spec_props = collect_spec_properties(spec_dict)
    observed = set(cluster_res.get("observed_union_fields", []))
    extra_fields = list(sorted(observed - spec_props))
    # If there are multiple extra fields not in the spec, treat as polymorphic candidate
    if len(extra_fields) >= 2:
        cluster_res["polymorphic_candidate"] = True
        cluster_res["extra_fields"] = extra_fields

    # 2. Reasoning Turn with Gemini
    prompt = f"""You are an expert API schema validator. Compare this OpenAPI spec with the runtime traffic data.
OpenAPI Spec:
{json.dumps(spec_dict, indent=2)}

Runtime Traffic Summary:
{json.dumps(cluster_res, indent=2)}

Task: Identify if there is schema drift. Choose the EXACT matching drift_type from this list:
- "SHADOW_HEADER" (e.g. idempotency-key header sent in requests but missing in spec)
- "TYPE_WIDENING" (e.g. zip_code string instead of integer)
- "NULLABILITY_DRIFT" (e.g. required field returned as null)
- "ENUM_DRIFT" (e.g. new enum value not in spec list)
- "STATUS_CODE_DRIFT" (e.g. 204 returned instead of 200)
- "ERROR_SCHEMA_DRIFT" (e.g. 401 error response body changed to errors array)
- "NESTED_SHADOW_FIELD" (e.g. extra field inside nested data object)
- "POLYMORPHIC_SHADOW_FIELD" (e.g. multiple dynamic fields like org_type and vat_number not in spec)
- "NONE" (if traffic matches spec or clean control)

Return JSON ONLY:
{{
  "drift_detected": true/false,
  "drift_type": "EXACT_TYPE_FROM_LIST",
  "field": "exact_field_name_or_none"
}}"""

    # If our deterministic tool flagged polymorphic fields, nudge the model
    if cluster_res.get("polymorphic_candidate"):
        prompt += "\n\nNOTE: The traffic logs show multiple variable/optional fields (variable_fields: " + ", ".join(cluster_res.get("variable_fields", [])) + "). If these are not defined in the spec, prefer the drift_type POLYMORPHIC_SHADOW_FIELD."

    result = safe_generate_json(
        client,
        model="models/gemini-3.1-flash-lite",
        contents=prompt,
        config={"response_mime_type": "application/json", "temperature": 0.0},
        max_retries=4,
    )

    obs.record_step("FINAL_VERDICT", result)
    obs.export_trajectory()
    return result