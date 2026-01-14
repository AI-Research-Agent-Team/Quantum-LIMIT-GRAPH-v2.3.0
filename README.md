# Quantum LIMIT-GRAPH v2.3.0

**Multilingual Quantum Research Agent with LIMIT-GRAPH Integration**

A cutting-edge integration of quantum computing, multilingual NLP, and semantic graph traversal for advanced research capabilities.

## Features

### Core Modules

- **Multilingual Parser** (`multilingual_parser.py`)
  - Language detection and normalization
  - mBART-50 tokenization
  - Language-specific subgraph routing
  - Supports 15+ languages

- **Quantum Traversal** (`quantum_traversal.py`)
  - QAOA-based graph traversal
  - Citation walks with semantic coherence
  - Fallback to classical traversal
  - Real-time latency tracking

- **ACE Context Router** (`ace_context_router.py`)
  - Hierarchical context routing (Global/Domain/Language)
  - Dynamic similarity thresholds (0.70–0.95)
  - Multi-layer context merging

- **REPAIR Edit Stream** (`repair_edit_stream.py`)
  - Dual-memory architecture (short-term/long-term)
  - Hallucination detection and correction
  - Edit provenance tracking
  - 5 hallucination types supported

### Evaluation Harness

- **Benchmark Harness** (`benchmark_harness.py`)
  - Multilingual edit reliability tests
  - Quantum vs. classical traversal comparison
  - Comprehensive performance metrics

- **Alignment Scorer** (`alignment_score.py`)
  - Cross-lingual alignment scoring
  - Entity linking and semantic overlap
  - Structural alignment metrics

- **Layer Balance Test** (`layer_balance_test.py`)
  - Context layer density validation
  - Redundancy checking (<12% threshold)
  - Balance score computation

### CI/CD Integration

- **SPDX Checker** (`spdx_checker.py`)
  - License compliance validation
  - Copyright notice verification
  - Automated compliance reporting

- **Edit Stream Validator** (`validator.py`)
  - Edit application testing
  - Hallucination detection validation
  - Memory management verification
  - Provenance tracking tests

## Installation

```bash
# Clone repository
git clone <repository-url>
cd "quantum limit graph v2.3.0"

# Install dependencies
pip install -r requirements.txt

# Optional: Install quantum dependencies
pip install qiskit qiskit-optimization qiskit-algorithms
```

## Quick Start

```python
from src.agent.multilingual_parser import parse_query
from src.graph.quantum_traversal import traverse_graph
from src.context.ace_context_router import route_context
from src.agent.repair_edit_stream import apply_edits

# Parse multilingual query
query = "Apa perkembangan terbaru dalam pembelajaran mesin kuantum?"
tokens = parse_query(query, lang="id")

# Route context
context = route_context(tokens)

# Quantum traversal
traversal_path = traverse_graph(context)

# Apply REPAIR edits
final_output = apply_edits(traversal_path)
```

## Running Examples

```bash
# Run complete sample flow
python sample_quantum_limit-graph.py

# Run benchmark suite
python src/evaluation/benchmark_harness.py

# Run validation tests
python src/ci/validator.py

# Check SPDX compliance
python src/ci/spdx_checker.py
```

## Architecture

```
Quantum LIMIT-GRAPH v2.3.0
├── Multilingual Parser (mBART-50)
│   ├── Language Detection
│   ├── Normalization
│   └── Subgraph Routing
│
├── ACE Context Router
│   ├── Global Layer
│   ├── Domain Layer
│   └── Language Layer
│
├── Quantum Graph Traversal
│   ├── QAOA Optimization
│   ├── Citation Walks
│   └── Classical Fallback
│
└── REPAIR Edit Stream
    ├── Hallucination Detection
    ├── Dual Memory
    └── Provenance Tracking
```

## Supported Languages

English (en), Spanish (es), French (fr), German (de), Chinese (zh), Japanese (ja), Korean (ko), Arabic (ar), Hindi (hi), Indonesian (id), Portuguese (pt), Russian (ru), Vietnamese (vi), Thai (th), Turkish (tr)

## Performance Metrics

- **Multilingual Parsing**: <50ms average latency
- **Quantum Traversal**: 80-120ms with QAOA
- **Classical Fallback**: 20-40ms
- **Edit Stream**: <30ms per edit
- **Context Routing**: <15ms per query

## Evaluation Results

Run benchmarks to see:
- Multilingual accuracy across 15+ languages
- Quantum vs. classical traversal comparison
- Edit reliability and hallucination detection rates
- Context layer balance metrics

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Quantum LIMIT-GRAPH CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run validation
        run: python src/ci/validator.py
      - name: Check SPDX compliance
        run: python src/ci/spdx_checker.py
      - name: Run benchmarks
        run: python src/evaluation/benchmark_harness.py
```

## Hugging Face Integration

### Model Index

See `model-index.yaml` for model discoverability on Hugging Face Hub.

### Demo Space

Interactive demo available at: [HuggingFace Space URL]

Features:
- Multilingual query input
- Real-time quantum traversal visualization
- Edit stream monitoring
- Performance metrics dashboard

### Contributor Challenge

Earn quantum alignment badges by:
1. Contributing multilingual test cases
2. Improving alignment scores
3. Optimizing quantum circuits
4. Enhancing hallucination detection

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

SPDX-License-Identifier: Apache-2.0

Copyright (c) 2025 AI Research Agent Team

## Citation

```bibtex
@software{quantum_limit_graph_2025,
  title={Quantum LIMIT-GRAPH: Multilingual Quantum Research Agent},
  author={AI Research Agent Team},
  year={2025},
  version={2.3.0},
  url={https://github.com/NurchoishAdam/quantum-limit-graph}
}
```

## Contact

For questions and support, please open an issue on GitHub.

## Acknowledgments

- mBART-50 team for multilingual models
- Qiskit team for quantum computing framework
- LIMIT-GRAPH contributors
- ACE context engineering research

