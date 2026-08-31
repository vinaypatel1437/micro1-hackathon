# Tools & Libraries Used

This document discloses all significant tools, models, and libraries used to develop and run DarkContract-Sentinel.

- Agent / Model: Google Gemini family via `google.genai` SDK (model used: `models/gemini-3.1-flash-lite` but any supported model listed by ModelService.ListModels is acceptable).
- Python runtime: CPython 3.11.
- Key Python libraries: `google-genai` SDK, `tenacity` (via SDK), `openinference` instrumentation, `phoenix` (Arize Phoenix UI), `PyYAML`, `tabulate`, `PyPDF2` (used for local PDF extraction), `python-dotenv`.
- Observability: `tracer.py` uses `openinference.instrumentation.google_genai.GoogleGenAIInstrumentor` and optionally launches local Phoenix UI when `PHOENIX_UI=1`.
- Local tools: `evaluate.py` drives runs and writes `trajectories/` artifacts.
 - Local tools: `evaluate.py` / `run_eval.py` drives runs and writes `trajectories/` artifacts.

Notes:
- All agent-use traces are recorded locally in `trajectories/` and can be shared with judges per submission rules. Keep your API keys and any private data out of the submission.
- The repo includes deterministic fallbacks so the evaluation completes even without a live API key; live LLM calls improve realism but are not required for judges to reproduce functional behavior.
 - The verifier (`verifier_agent.py`) uses the `jsonschema` package. Install it with `pip install jsonschema` or add it to your dependency list.
