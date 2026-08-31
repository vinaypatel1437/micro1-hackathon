# Improvement Changelog

This changelog records major iterations and why they were made. Each entry links to the evidence (trajectories, diffs) that motivated the change.

- 2026-08-28: Initial repository scaffold with `agent_workflow.py`, `baseline.py`, `evaluate.py`, and 10 example `data/*` cases.
- 2026-08-29: Added `llm_utils.safe_generate_json` to retry on 429 RESOURCE_EXHAUSTED and provide deterministic fallback when API quota is exhausted. Evidence: `trajectories/*` where fallback outputs were used when needed.
- 2026-08-29: Patched `phoenix` instrumentation in local venv to avoid dataclass default mutation error on Windows. Evidence: local run logs and updated `tracer.py` gating for `PHOENIX_UI`.
- 2026-08-30: Implemented deterministic heuristic in `agent_workflow.py` to detect polymorphic shadow fields by comparing observed response keys against spec properties; added prompt nudge when polymorphic candidates are found. Evidence: `trajectories/case_10_trajectory.md` showing corrected classification.
- 2026-08-30: Baseline now records agent trajectories using `AgentObservability` to meet the requirement of submitting trajectories for every agent used.
- 2026-08-31: Added `run_eval.py` wrapper so judges can run `python run_eval.py` per hackathon instructions.
- 2026-08-31: Added deterministic fallbacks and documentation updates (`README.md`, `REPRODUCTION.md`, `TOOLS_USED.md`) to improve reproducibility for offline judging.
- 2026-08-31: Added `verifier_agent.py` — an offline verifier that validates observed traffic against the OpenAPI schema and produces `trajectories/*_verifier.*` reports.

Notes:
- The repository includes `trajectories/` for agent and baseline traces for each case.
- For trace acquisition reimbursement or external validation, see `REPRODUCTION.md` and contact the organizers as required.
