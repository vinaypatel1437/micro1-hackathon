# DarkContract-Sentinel (micro1-hackathon)

DarkContract-Sentinel evaluates API schema drift by comparing OpenAPI specifications against observed runtime traffic and classifying drift types. It includes a baseline LLM flow, an agent-based workflow, and a lightweight offline verifier for replay validation.

Key drift types detected:

- Shadow headers
- Type widening / nullability changes
- Enum drift
- Status-code drift
- Error-schema drift
- Nested shadow fields
- Polymorphic shadow fields

**Status:** Ready for micro1 submission — includes baseline, agent, and verifier components.

## Features

- Deterministic tooling to reproduce runs without a live LLM key
- Resilient LLM wrapper with retry/backoff and deterministic fallbacks
- Exportable trajectories (JSON + Markdown) for judge inspection
- `verifier_agent.py` for offline schema validation using OpenAPI + `jsonschema`

## Quickstart

1. Create and activate a virtual environment:

```powershell
python -m venv ./venv
./venv/Scripts/activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. (Optional) Add `GEMINI_API_KEY` to a `.env` file for live LLM runs.

4. Run the full evaluation (baseline + agent):

```powershell
python run_eval.py
```

Outputs:

- Console: table with per-case baseline vs agent results and an accuracy summary
- `trajectories/`: JSON and Markdown traces for each case (required for submission)

## Verifier (optional)

Run the verifier on a single case:

```powershell
python verifier_agent.py --case data/case_10
```

Run the verifier for all cases:

```powershell
python verifier_agent.py --all
```

## Contributing

If you want to improve the project, open an issue or submit a PR. Keep changes focused on reproducibility and minimal external services.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contact

For questions or reproducibility artifacts (pinned requirements, Dockerfile, recorded transcripts), contact the maintainer at patel.vp.vinay@gmail.com.

## Repository layout

- `agent_workflow.py`: Agent flow that runs deterministic tools, composes LLM prompts, and records agent trajectories via `tracer.py`.
- `baseline.py`: Baseline LLM flow (records baseline trajectories).
- `evaluate.py`: Runs the benchmark across `data/*` cases and prints a comparison table.
- `run_eval.py`: Small wrapper to run the evaluation per hackathon instructions (`python run_eval.py`).
- `tracer.py`: `AgentObservability` utilities to capture and export trajectory JSON/Markdown files and optionally launch Phoenix UI when `PHOENIX_UI=1`.
- `data/`: 10 benchmark case folders with `openapi.yaml`, `traffic.jsonl`, and `ground_truth.json`.
- `trajectories/`: Generated `.md` and `.json` traces for agent and baseline runs.
- `IMPROVEMENT_CHANGELOG.md`, `TOOLS_USED.md`: Submission documentation and tool disclosure.

## Quick start (reproducible)

1. Create and activate Python 3.11 virtual environment:

```powershell
python -m venv ./venv
./venv/Scripts/activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add your API key to `.env` (optional for offline deterministic fallback):

```
GEMINI_API_KEY=YOUR_KEY_HERE
```

4. Run the evaluation (recommended):

```powershell
python run_eval.py
```

Outputs

- Console: per-case comparison table and summary accuracies.
- `trajectories/`: `.md` and `.json` artifacts for each case and for both baseline and agent runs (required for submission).

## Phoenix UI (optional)

- To enable the local Phoenix UI for interactive inspection set `PHOENIX_UI=1` then run the evaluation. On Windows, Phoenix may leave a locked temp DB; if you see a PermissionError, unset `PHOENIX_UI` or restart the Python process.

## Submission checklist (micro1)

- Baseline + Agent: Present (`baseline.py`, `agent_workflow.py`).
- 10-case benchmark: Present (`data/` folder). Use `generate_dataset.py` to recreate if needed.
- Agent trajectories: Present under `trajectories/` — both baseline and agent traces are included.
- Reproduction guide: `REPRODUCTION.md` (this repo).
- Improvement changelog and tools disclosure: `IMPROVEMENT_CHANGELOG.md`, `TOOLS_USED.md`.

## Notes & limitations

- The repository includes a deterministic `extract_log_clusters` clusterer and a heuristic for polymorphic shadow fields used to nudge model outputs. A lightweight sandboxed HTTP simulator/verifier is not included in this submission; adding a `verifier_agent` that replays requests in a local sandbox is recommended for full verification pipelines.

## License

- MIT License (see `LICENSE`)
