# Trajectory Log: `case_10`

- **Runtime:** 7.51s
- **Total Iterations:** 4

---

### Step 1: `INITIALIZE` (+3.74s)
```json
{
  "case_id": "case_10",
  "spec": {
    "paths": {
      "/v1/org": {
        "patch": {
          "responses": {
            "200": {
              "content": {
                "application/json": {
                  "schema": {
                    "properties": {
                      "tax_id": {
                        "type": "string"
                      }
                    }
                  }
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

### Step 2: `TOOL_CALL` (+3.74s)
```json
{
  "tool": "extract_log_clusters",
  "args": {
    "case_id": "case_10"
  }
}
```

### Step 3: `TOOL_RESPONSE` (+3.74s)
```json
{
  "result": {
    "is_spam": false,
    "status_code": 200,
    "headers": [],
    "body_fields": {
      "tax_id": "99-123",
      "org_type": "ENTERPRISE",
      "vat_number": "GB999"
    },
    "observed_union_fields": [
      "org_type",
      "tax_id",
      "vat_number"
    ],
    "observed_common_fields": [
      "org_type",
      "tax_id",
      "vat_number"
    ],
    "variable_fields": [],
    "polymorphic_candidate": true,
    "extra_fields": [
      "org_type",
      "vat_number"
    ]
  }
}
```

### Step 4: `FINAL_VERDICT` (+7.509s)
```json
{
  "drift_detected": true,
  "drift_type": "POLYMORPHIC_SHADOW_FIELD",
  "field": "org_type, vat_number"
}
```

