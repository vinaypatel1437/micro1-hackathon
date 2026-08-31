# Trajectory Log: `case_01`

- **Runtime:** 5.45s
- **Total Iterations:** 4

---

### Step 1: `INITIALIZE` (+2.635s)
```json
{
  "case_id": "case_01",
  "spec": {
    "paths": {
      "/v1/payments": {
        "post": {
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "properties": {
                    "amount": {
                      "type": "number"
                    }
                  },
                  "type": "object"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Step 2: `TOOL_CALL` (+2.635s)
```json
{
  "tool": "extract_log_clusters",
  "args": {
    "case_id": "case_01"
  }
}
```

### Step 3: `TOOL_RESPONSE` (+2.635s)
```json
{
  "result": {
    "is_spam": false,
    "status_code": 200,
    "headers": [
      "idempotency-key"
    ],
    "body_fields": {
      "amount": 100
    },
    "observed_union_fields": [
      "amount"
    ],
    "observed_common_fields": [
      "amount"
    ],
    "variable_fields": [],
    "polymorphic_candidate": false
  }
}
```

### Step 4: `FINAL_VERDICT` (+5.439s)
```json
{
  "drift_detected": true,
  "drift_type": "SHADOW_HEADER",
  "field": "idempotency-key"
}
```

