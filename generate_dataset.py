# generate_dataset.py
import json
import yaml
from pathlib import Path

def create_dataset():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    cases = [
        ("case_01", "POST /v1/payments (Shadow Header)", 
         {"paths": {"/v1/payments": {"post": {"requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"amount": {"type": "number"}}}}}}}}}},
         [{"status": 200, "headers": {"idempotency-key": "uuid-123"}, "body": {"amount": 100}} for _ in range(15)],
         {"drift": True, "type": "SHADOW_HEADER", "field": "idempotency-key"}),

        ("case_02", "GET /v1/users/{id} (Type Widening)",
         {"paths": {"/v1/users/{id}": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"properties": {"zip_code": {"type": "integer"}}}}}}}}}}},
         [{"status": 200, "body": {"zip_code": "EC1A 1BB"}} for _ in range(15)],
         {"drift": True, "type": "TYPE_WIDENING", "field": "zip_code"}),

        ("case_03", "PUT /v1/subs (Nullability Drift)",
         {"paths": {"/v1/subs": {"put": {"responses": {"200": {"content": {"application/json": {"schema": {"properties": {"active": {"type": "boolean"}}, "required": ["active"]}}}}}}}}},
         [{"status": 200, "body": {"active": None}} for _ in range(15)],
         {"drift": True, "type": "NULLABILITY_DRIFT", "field": "active"}),

        ("case_04", "POST /v1/orders (Enum Drift)",
         {"paths": {"/v1/orders": {"post": {"responses": {"200": {"content": {"application/json": {"schema": {"properties": {"status": {"type": "string", "enum": ["PENDING", "COMPLETED"]}}}}}}}}}}},
         [{"status": 200, "body": {"status": "PARTIALLY_REFUNDED"}} for _ in range(15)],
         {"drift": True, "type": "ENUM_DRIFT", "field": "status"}),

        ("case_05", "DELETE /v1/items (Status Code Drift)",
         {"paths": {"/v1/items/{id}": {"delete": {"responses": {"200": {"description": "OK"}}}}}},
         [{"status": 204, "body": None} for _ in range(15)],
         {"drift": True, "type": "STATUS_CODE_DRIFT", "field": "204"}),

        ("case_06", "GET /v1/inventory (Clean Control)",
         {"paths": {"/v1/inventory": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"properties": {"count": {"type": "integer"}}}}}}}}}}},
         [{"status": 200, "body": {"count": 42}} for _ in range(15)],
         {"drift": False, "type": "NONE", "field": "none"}),

        ("case_07", "POST /v1/auth (Error Schema Drift)",
         {"paths": {"/v1/auth": {"post": {"responses": {"401": {"content": {"application/json": {"schema": {"properties": {"error": {"type": "string"}}}}}}}}}}},
         [{"status": 401, "body": {"errors": [{"code": "BAD_PASS"}]}} for _ in range(15)],
         {"drift": True, "type": "ERROR_SCHEMA_DRIFT", "field": "errors"}),

        ("case_08", "GET /v1/analytics (Nested Shadow Field)",
         {"paths": {"/v1/analytics": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"properties": {"data": {"properties": {"dim": {"type": "string"}}}}}}}}}}}}},
         [{"status": 200, "body": {"data": {"dim": "US", "dimension_id": 99}}} for _ in range(15)],
         {"drift": True, "type": "NESTED_SHADOW_FIELD", "field": "dimension_id"}),

        ("case_09", "POST /v1/webhooks (400 Spam - False Drift)",
         {"paths": {"/v1/webhooks": {"post": {"requestBody": {"content": {"application/json": {"schema": {"properties": {"event": {"type": "string"}}}}}}, "responses": {"200": {}}}}}},
         [{"status": 400, "body": {"invalid": True}} for _ in range(15)],
         {"drift": False, "type": "NONE", "field": "none"}),

        ("case_10", "PATCH /v1/org (Adversarial Polymorphism)",
         {"paths": {"/v1/org": {"patch": {"responses": {"200": {"content": {"application/json": {"schema": {"properties": {"tax_id": {"type": "string"}}}}}}}}}}},
         [{"status": 200, "body": {"tax_id": "99-123", "org_type": "ENTERPRISE", "vat_number": "GB999"}} for _ in range(15)],
         {"drift": True, "type": "POLYMORPHIC_SHADOW_FIELD", "field": "vat_number"})
    ]

    for cid, name, spec, logs, truth in cases:
        folder = data_dir / cid
        folder.mkdir(exist_ok=True)
        with open(folder / "openapi.yaml", "w", encoding="utf-8") as f:
            yaml.dump(spec, f)
        with open(folder / "traffic.jsonl", "w", encoding="utf-8") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")
        with open(folder / "ground_truth.json", "w", encoding="utf-8") as f:
            json.dump({"name": name, **truth}, f, indent=2)

    print("✅ Created 10 Benchmark Test Cases in /data")

if __name__ == "__main__":
    create_dataset()