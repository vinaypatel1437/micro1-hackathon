"""verifier_agent.py

Lightweight verifier/simulator for offline verification of observed traffic
against the OpenAPI spec. Produces a simple acceptance summary and writes
results to `trajectories/<case>_verifier.json` and Markdown.

Usage:
  python verifier_agent.py --case data/case_10
  python verifier_agent.py --all
"""
import argparse
import json
from pathlib import Path
import yaml

try:
    import jsonschema
except Exception:
    jsonschema = None


def load_spec_schema(spec: dict):
    # Try to extract the first response schema (200) or requestBody schema
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, body in methods.items():
            # responses
            responses = body.get("responses", {})
            if responses:
                for code, resp in responses.items():
                    if isinstance(resp, dict):
                        content = resp.get("content", {})
                        app_json = content.get("application/json") or content.get("application/json; charset=utf-8")
                        if app_json and isinstance(app_json, dict):
                            schema = app_json.get("schema")
                            if schema:
                                return schema
            # requestBody
            rb = body.get("requestBody")
            if rb and isinstance(rb, dict):
                content = rb.get("content", {})
                app_json = content.get("application/json")
                if app_json:
                    schema = app_json.get("schema")
                    if schema:
                        return schema
    return None


def to_jsonschema(schema: dict) -> dict:
    # The OpenAPI subschema is commonly JSON Schema compatible for our benchmark.
    # Ensure top-level object type and enforce strictness when requested.
    js = dict(schema) if schema else {}
    if "type" not in js:
        js["type"] = "object"
    return js


def verify_case(case_dir: Path, output_dir: Path = Path("trajectories")):
    case_id = case_dir.name
    spec_path = case_dir / "openapi.yaml"
    logs_path = case_dir / "traffic.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    schema = load_spec_schema(spec)
    if schema is None:
        print(f"[{case_id}] No JSON schema found in spec; skipping verification.")
        return

    jschema = to_jsonschema(schema)

    if jsonschema is None:
        print("jsonschema package not found. Install with `pip install jsonschema` to run verifier.")
        return

    total = 0
    strict_valid = 0
    permissive_valid = 0

    # Strict schema: disallow additional properties to simulate a strict backend
    strict_schema = dict(jschema)
    strict_schema["additionalProperties"] = False

    # Permissive schema: allow additional properties
    permissive_schema = dict(jschema)
    permissive_schema["additionalProperties"] = True

    with open(logs_path, "r", encoding="utf-8") as f:
        for line in f:
            total += 1
            try:
                log = json.loads(line)
            except Exception:
                continue
            body = log.get("body") or log.get("response_body") or log.get("request_body") or {}
            if not isinstance(body, dict):
                # non-dict bodies are treated as valid for our simple checks
                strict_valid += 1
                permissive_valid += 1
                continue

            try:
                jsonschema.validate(instance=body, schema=permissive_schema)
                permissive_valid += 1
            except jsonschema.ValidationError:
                pass

            try:
                jsonschema.validate(instance=body, schema=strict_schema)
                strict_valid += 1
            except jsonschema.ValidationError:
                pass

    permissive_pct = (permissive_valid / total) * 100 if total else 0
    strict_pct = (strict_valid / total) * 100 if total else 0

    # Heuristic verdict:
    # - If permissive_pct is high (>=80) and strict_pct is low (<50), backend likely accepts shadow fields.
    if permissive_pct >= 80 and strict_pct < 50:
        verdict = {
            "verdict": "BACKEND_PERMISSIVE",
            "message": "Observed traffic contains fields not in spec and permissive validation passes while strict fails. Backend likely accepts shadow fields.",
        }
    else:
        verdict = {
            "verdict": "BACKEND_STRICT_OR_INCONCLUSIVE",
            "message": "Observed traffic mostly conforms to spec under permissive/strict checks, or insufficient evidence of shadow acceptance.",
        }

    summary = {
        "case_id": case_id,
        "total_requests": total,
        "permissive_valid": permissive_valid,
        "strict_valid": strict_valid,
        "permissive_pct": round(permissive_pct, 1),
        "strict_pct": round(strict_pct, 1),
        **verdict,
    }

    # Write JSON and Markdown artifacts to trajectories/
    out_json = output_dir / f"{case_id}_verifier.json"
    out_md = output_dir / f"{case_id}_verifier.md"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# Verifier Report: `{case_id}`\n\n")
        f.write(f"- Total requests inspected: {total}\n")
        f.write(f"- Permissive validation passed: {permissive_valid} ({summary['permissive_pct']}%)\n")
        f.write(f"- Strict validation passed: {strict_valid} ({summary['strict_pct']}%)\n\n")
        f.write(f"**Verdict**: {summary['verdict']}\n\n")
        f.write(summary['message'] + "\n")

    print(f"[{case_id}] Verifier report written to {out_json} and {out_md}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=str, help="Path to a single case directory (e.g. data/case_10)")
    parser.add_argument("--all", action="store_true", help="Run verifier on all cases under data/")
    args = parser.parse_args()

    data_dir = Path("data")
    if args.case:
        case_dir = Path(args.case)
        if not case_dir.exists():
            print(f"Case directory {case_dir} does not exist")
            return
        verify_case(case_dir)
    elif args.all:
        for d in sorted(data_dir.iterdir()):
            if d.is_dir():
                verify_case(d)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
