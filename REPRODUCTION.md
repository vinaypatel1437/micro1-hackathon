## Reproducing Evaluation (DarkContract-Sentinel)

This file provides exact commands and troubleshooting steps so judges can reproduce the results from a clean environment.

Prerequisites
- Python 3.11 (tested)
- Git (optional)
- A Google Gemini API key (optional — repository contains deterministic fallbacks; live LLM calls require a key).

Quick reproduction (bare minimum)
1. From the repo root, create and activate a venv

```powershell
python -m venv ./venv
./venv/Scripts/activate
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. (Optional) Add `GEMINI_API_KEY` to a `.env` file in the repo root for live LLM runs

```
GEMINI_API_KEY=YOUR_KEY_HERE
```

4. Run the full evaluation (baseline + agent)

```powershell
python run_eval.py
```

What to expect
- Console: a table with per-case baseline vs agent results and an accuracy summary.
- `trajectories/`: markdown and JSON traces for both baseline and agent, one file per case (required for submission).

Recreating the dataset
- If you want to recreate the benchmark cases, run:

```powershell
python generate_dataset.py
```

Re-running a single case
- To run the agent on a specific case directory (useful during development):

```powershell
python -c "from agent_workflow import run_agent_on_case; from pathlib import Path; print(run_agent_on_case(Path('data/case_10')))"
```

Troubleshooting
- 429 RESOURCE_EXHAUSTED: This indicates API quota or billing limits. Options:
	- Wait and retry (the repo's `llm_utils.safe_generate_json` will retry transient 429s).
	- Use a different supported model listed by ModelService.ListModels.
	- Run offline: the code includes deterministic fallbacks so evaluation will complete even without a live key.
- 404 NOT_FOUND for model id: Use `client.models.list()` (ModelService.ListModels) to choose a supported model and update `agent_workflow.py` / `baseline.py`.
- Phoenix DB locked on Windows: unset `PHOENIX_UI` (default is off), or reboot the Python process after stopping Phoenix to release handles.

Notes for judges
- Trajectories are self-contained and explain the deterministic tool outputs, prompt used, LLM response (or fallback), and final verdict. See `trajectories/`.
- The repository does not include a networked sandbox verifier by default; the agent uses deterministic heuristics to verify polymorphic fields. A simple sandboxed HTTP verifier can be added as `verifier_agent.py` if required for runtime replay verification.

Verifier (optional, recommended)
- The repo includes `verifier_agent.py`, a lightweight offline verifier that validates observed traffic against the OpenAPI schema using `jsonschema` and writes reports to `trajectories/`.
- Install `jsonschema` if not present:

```powershell
pip install jsonschema
```

- Run verifier for a single case:

```powershell
python verifier_agent.py --case data/case_10
```

- Run verifier for all cases:

```powershell
python verifier_agent.py --all
```


Contact
- If you need additional reproducibility artifacts (pinned requirements, Dockerfile, or recorded LLM transcripts), ask and I will add them.
