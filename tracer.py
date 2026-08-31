import os
import json
import time
from pathlib import Path
import phoenix as px
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider

class AgentObservability:
    def __init__(self, case_id: str, output_dir: str = "trajectories"):
        self.case_id = case_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.start_time = time.time()
        self.steps = []

        # 1. Optionally start Local Phoenix UI (set PHOENIX_UI=1 to enable)
        try:
            if os.getenv('PHOENIX_UI', '0') == '1':
                px.launch_app()
                tracer_provider = TracerProvider()
                trace_api.set_tracer_provider(tracer_provider)
                GoogleGenAIInstrumentor().instrument()
        except Exception:
            # If Phoenix is already running or instrumentation fails, continue without crashing.
            pass

    def record_step(self, step_type: str, details: dict):
        """Records agent actions, tool calls, and verifier decisions."""
        entry = {
            "timestamp": round(time.time() - self.start_time, 3),
            "step_type": step_type,
            "details": details
        }
        self.steps.append(entry)

    def export_trajectory(self):
        """Saves JSON and Markdown logs to /trajectories/."""
        # 1. JSON Export
        json_file = self.output_dir / f"{self.case_id}_trajectory.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "case_id": self.case_id,
                "runtime_seconds": round(time.time() - self.start_time, 2),
                "total_steps": len(self.steps),
                "steps": self.steps
            }, f, indent=2)

        # 2. Markdown Export (Judges can read directly on GitHub)
        md_file = self.output_dir / f"{self.case_id}_trajectory.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# Trajectory Log: `{self.case_id}`\n\n")
            f.write(f"- **Runtime:** {round(time.time() - self.start_time, 2)}s\n")
            f.write(f"- **Total Iterations:** {len(self.steps)}\n\n---\n\n")
            for idx, s in enumerate(self.steps, 1):
                f.write(f"### Step {idx}: `{s['step_type']}` (+{s['timestamp']}s)\n")
                f.write(f"```json\n{json.dumps(s['details'], indent=2)}\n```\n\n")

        print(f"✅ Trajectory written to {md_file}")
        # No-op: we do not attempt to force-shutdown Phoenix here; leave it
        # to external tooling or the Phoenix process itself.