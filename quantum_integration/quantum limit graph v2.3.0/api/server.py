from fastapi import FastAPI, BackgroundTasks
from benchmarks.runner import BenchmarkRunner
from pydantic import BaseModel

app = FastAPI(title="Quantum-LIMIT Agent")

class TaskInput(BaseModel):
    task_id: str
    graph_parameters: dict

# AgentBeats Standard Endpoint
@app.post("/agent/tasks")
async def solve_task(task: TaskInput, background_tasks: BackgroundTasks):
    """
    Receives a graph problem from the Judge (Green Agent).
    """
    # 1. Parse the complex graph parameters
    scenario = {
        "id": task.task_id,
        "nodes": task.graph_parameters.get("nodes", 10),
        "type": "quantum_limit"
    }
    
    # 2. Run the specialized solver (using our benchmark logic)
    runner = BenchmarkRunner([scenario])
    result = runner.run_single_scenario(scenario)
    
    # 3. Return formatted answer
    return {
        "status": "completed",
        "result": {
            "optimized_value": result['energy_gap'],
            "confidence": result['accuracy']
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ready", "gpu_available": True}
