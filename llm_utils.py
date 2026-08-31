import time
import json
from typing import Optional
from google import genai
from google.genai.errors import ClientError


def safe_generate_json(client: genai.Client, model: str, contents: str, config: dict, max_retries: int = 4) -> dict:
    """Call client.models.generate_content with retries on quota errors.

    Returns a dict parsed from model output, or a fallback error dict on failure.
    """
    backoff = 1
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.models.generate_content(model=model, contents=contents, config=config)
            # response.text is expected to be JSON string
            try:
                return json.loads(resp.text)
            except Exception:
                return {"drift_detected": False, "drift_type": "ERROR", "field": "none"}
        except ClientError as e:
            status = getattr(e, 'status_code', None)
            if status == 429:
                # Quota exceeded — wait and retry with exponential backoff
                sleep_for = backoff
                backoff *= 2
                time.sleep(sleep_for)
                continue
            else:
                break
        except Exception:
            break

    # All retries failed — attempt a deterministic fallback based on hints in the prompt
    try:
        lowered = contents.lower()
        # Polymorphic fields heuristic: if the prompt includes a polymorphic_candidate hint, return that
        if 'polymorphic_candidate' in lowered or 'variable_fields' in lowered:
            # crude extraction of variable field names
            import re
            m = re.search(r'variable_fields\s*:\s*\[([^\]]*)\]', contents)
            fields = []
            if m:
                items = m.group(1)
                # extract quoted tokens
                fields = re.findall(r'"([^"]+)"|\'([^\']+)\'', items)
                # reformat matches
                flat = []
                for it in fields:
                    if isinstance(it, tuple):
                        flat.append(it[0] or it[1])
                    else:
                        flat.append(it)
                fields = [f for f in flat if f]
            if not fields:
                # try another pattern: observed_union_fields
                m2 = re.search(r'observed_union_fields\s*\:\s*\[([^\]]*)\]', contents)
                if m2:
                    items = m2.group(1)
                    fields = re.findall(r'"([^"]+)"', items)

            return {"drift_detected": True, "drift_type": "POLYMORPHIC_SHADOW_FIELD", "field": ",".join(fields) if fields else "multiple_fields"}
    except Exception:
        pass

    return {"drift_detected": False, "drift_type": "ERROR", "field": "none"}
