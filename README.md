# Quantum LIMIT-GRAPH for AgentX-AgentBeats Competition

**Multilingual Quantum Research Agent Benchmark**

A green agent (evaluator/benchmark) for the AgentX-AgentBeats Competition that evaluates AI agents on multilingual research capabilities, quantum-enhanced graph traversal, and hallucination detection.

## 🎯 Overview

Quantum LIMIT-GRAPH is a comprehensive benchmark for assessing AI agents across:

- **Multilingual Understanding**: Tests comprehension across 15+ languages (English, Spanish, French, German, Chinese, Japanese, Korean, Arabic, Hindi, Indonesian, Portuguese, Russian, Vietnamese, Thai, Turkish)
- **Semantic Graph Traversal**: Evaluates quantum vs classical traversal algorithms
- **Context Routing**: Assesses hierarchical context management (Global/Domain/Language layers)
- **Hallucination Detection**: Measures accuracy in identifying and avoiding factual errors
- **Performance Metrics**: Tracks latency, semantic coherence, and quantum speedup

## 🏆 Competition Track

**Research Track - Agent Evaluation Benchmark**

This green agent evaluates purple agents (agents under test) on their ability to:
1. Parse and understand multilingual research queries
2. Navigate semantic knowledge graphs efficiently
3. Maintain semantic coherence across languages
4. Detect and avoid hallucinations
5. Optimize performance with quantum-enhanced algorithms

## 📋 Prerequisites

- Docker
- Python 3.11+
- 4GB RAM minimum
- AgentBeats account (register at https://agentbeats.dev)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/AI-Research-Agent-Team/Quantum-LIMIT-GRAPH-v2.3.0.git
cd Quantum-LIMIT-GRAPH-v2.3.0
```

### 2. Build Docker Image

```bash
docker build -t quantum-limit-graph:latest .
```

### 3. Run Locally

```bash
docker run -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e AGENT_PORT=8000 \
  quantum-limit-graph:latest
```

### 4. Test A2A Endpoint

```bash
# Check agent card
curl http://localhost:8000/.well-known/agent-card.json

# Health check
curl http://localhost:8000/health
```

## 📦 Repository Structure

```
Quantum-LIMIT-GRAPH-v2.3.0/
├── app.py                          # Main A2A-compliant agent server
├── Dockerfile                      # Container definition
├── requirements.txt                # Python dependencies
├── run.sh                          # Agent launch script
├── README.md                       # This file
├── quantum_integration/            # Core benchmark modules
│   ├── multilingual_parser.py     # Language detection & parsing
│   ├── quantum_traversal.py       # Quantum graph algorithms
│   ├── ace_context_router.py      # Context routing logic
│   └── repair_edit_stream.py      # Hallucination detection
└── .github/workflows/
    └── build-and-publish.yml       # CI/CD pipeline
```

## 🔧 Configuration

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `AGENT_PORT`: Server port (default: 8000)
- `OPENAI_API_KEY`: Optional, for enhanced evaluation
- `GOOGLE_API_KEY`: Optional, for additional models

### Agent Configuration

Modify agent behavior in `app.py`:

```python
AGENT_CARD = {
    "agent_info": {
        "id": "quantum-limit-graph-evaluator",
        "name": "Quantum LIMIT-GRAPH Benchmark",
        "version": "2.3.0",
        ...
    }
}
```

## 🎮 Running Evaluations

### Local Evaluation (without AgentBeats platform)

```python
import requests

# Create evaluation task
response = requests.post("http://localhost:8000/v1/tasks", json={
    "messages": [
        {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": "Apa perkembangan terbaru dalam pembelajaran mesin kuantum?"
                }
            ]
        },
        {
            "role": "agent",
            "parts": [
                {
                    "type": "text",
                    "text": "Your purple agent's response here..."
                }
            ]
        }
    ],
    "config": {
        "language": "id",
        "evaluation_mode": "comprehensive"
    }
})

task_id = response.json()["task_id"]

# Get results
results = requests.get(f"http://localhost:8000/v1/tasks/{task_id}")
print(results.json())
```

### AgentBeats Platform Integration

1. **Register Agent on AgentBeats**
   - Go to https://agentbeats.dev
   - Click "Register Agent"
   - Select "Green Agent" (Evaluator)
   - Provide Docker image reference

2. **Publish to GitHub Container Registry**

```bash
# Tag image
docker tag quantum-limit-graph:latest ghcr.io/YOUR_USERNAME/quantum-limit-graph:latest

# Push to registry
docker push ghcr.io/YOUR_USERNAME/quantum-limit-graph:latest
```

3. **Configure GitHub Actions**
   - Enable GitHub Actions in your repository
   - Set secrets: `GHCR_TOKEN`
   - Workflow will automatically build and publish on push

## 📊 Evaluation Metrics

The benchmark produces the following scores (0.0 - 1.0):

| Metric | Description | Weight |
|--------|-------------|--------|
| **Parsing Accuracy** | Successful multilingual tokenization | 20% |
| **Semantic Coherence** | Query-response semantic alignment | 25% |
| **Hallucination Avoidance** | Factual accuracy and citation quality | 25% |
| **Latency Performance** | Response time optimization | 15% |
| **Quantum Performance** | Speedup vs classical algorithms | 15% |

**Overall Score**: Weighted average of all metrics. Pass threshold: 0.60

### Sample Evaluation Output

```json
{
  "overall_score": 0.78,
  "passed": true,
  "scores": {
    "parsing_accuracy": 1.0,
    "semantic_coherence": 0.85,
    "hallucination_avoidance": 0.72,
    "latency_score": 0.80,
    "quantum_performance": 0.65
  },
  "metrics": {
    "detected_language": "id",
    "hallucination_rate": 0.028,
    "traversal_latency_ms": 87.3,
    "quantum_speedup": 1.3
  }
}
```

## 🧪 Testing Baseline Purple Agent

A baseline purple agent is included for testing:

```bash
# Run baseline evaluation
python examples/baseline_purple_agent.py
```

Expected baseline scores:
- Parsing Accuracy: 0.95+
- Semantic Coherence: 0.70+
- Hallucination Avoidance: 0.60+
- Overall: 0.65+

## 🔬 Advanced Features

### Quantum Traversal Evaluation

Enable quantum circuit simulation:

```python
evaluation_results = await evaluate_agent_response(
    query=query,
    agent_response=response,
    config={
        "enable_quantum": True,
        "qaoa_layers": 3,
        "classical_fallback": True
    }
)
```

### Multi-Language Testing

Batch evaluation across languages:

```python
languages = ["en", "es", "zh", "ja", "ar"]
for lang in languages:
    results = evaluate_multilingual(query, lang)
    print(f"{lang}: {results['overall_score']:.2f}")
```

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all quantum_integration modules are present
   - Run: `pip install -r requirements.txt`

2. **Port already in use**
   - Change AGENT_PORT: `docker run -p 8080:8080 -e AGENT_PORT=8080 ...`

3. **Quantum libraries not working**
   - Quantum features are optional
   - Set `enable_quantum: false` in config

4. **Out of memory**
   - Increase Docker memory limit to 4GB+
   - Reduce batch size in evaluation

## 📚 Documentation

- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [AgentBeats Tutorial](https://docs.agentbeats.dev/tutorial/)
- [Competition Guidelines](https://rdi.berkeley.edu/agentx-agentbeats.html)
- [Original Quantum LIMIT-GRAPH Repo](https://github.com/AI-Research-Agent-Team/Quantum-LIMIT-GRAPH-v2.3.0)

## 🤝 Contributing

Contributions are welcome! To participate in the competition:

1. Fork this repository
2. Create your feature branch: `git checkout -b feature/amazing-improvement`
3. Commit changes: `git commit -m 'Add amazing improvement'`
4. Push to branch: `git push origin feature/amazing-improvement`
5. Submit a Pull Request

### Competition Submission Checklist

- [ ] Green agent implements A2A protocol
- [ ] Docker image builds successfully
- [ ] Agent card accessible at `/.well-known/agent-card.json`
- [ ] Baseline purple agent included
- [ ] README with setup instructions
- [ ] Demo video (max 3 minutes)
- [ ] Registered on AgentBeats platform

## 📜 License

SPDX-License-Identifier: Apache-2.0

Copyright (c) 2025 AI Research Agent Team

## 🏅 Competition Details

- **Competition**: AgentX-AgentBeats 
- **Track**: Research Track - Agent Evaluation Benchmark
- **Category**: Multilingual Research Agent
- **Phase 1 Deadline**: Check official competition website
- **Prize Pool**: $1M+ in prizes and credits

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/AI-Research-Agent-Team/Quantum-LIMIT-GRAPH-v2.3.0/issues)
- **Competition Discord**: Join AgentX-AgentBeats Discord
- **Email**: [Competition organizers]

## 🙏 Acknowledgments

- Berkeley RDI for organizing AgentX-AgentBeats Competition
- A2A Protocol contributors
- Qiskit team for quantum computing framework
- mBART-50 team for multilingual models

---

**Ready to benchmark the next generation of AI agents? Let's go! 🚀**
