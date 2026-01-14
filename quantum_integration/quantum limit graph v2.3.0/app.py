import os
import subprocess
from fastapi import FastAPI
from typing import Optional

app = FastAPI(title="Quantum LIMIT-GRAPH v2.3.0")

def run_cmd(cmd: list[str]) -> dict:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"ok": True, "stdout": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"ok": False, "stdout": e.stdout, "stderr": e.stderr}

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.3.0"}

@app.post("/run/sample")
def run_sample():
    # Runs the complete sample flow
    return run_cmd(["python", "sample_quantum_limit-graph.py"])

@app.post("/run/benchmark")
def run_benchmark():
    # Runs benchmark suite
    return run_cmd(["python", "src/evaluation/benchmark_harness.py"])

@app.post("/run/validator")
def run_validator():
    # Runs CI validator
    return run_cmd(["python", "src/ci/validator.py"])

@app.post("/run/spdx")
def run_spdx():
    # Runs SPDX compliance checker
    return run_cmd(["python", "src/ci/spdx_checker.py"])

if __name__ == "__main__":
    # Default to API server; can be swapped to Gradio if preferred
    import uvicorn
    port = int(os.environ.get("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
