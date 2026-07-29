# ADR — Agentic Detection and Response

ADR is an open-source telemetry sensor and dual-agent benchmark/detection framework for securing AI agents that use the Model Context Protocol (MCP).

Research artifacts for **[ADR: An Agentic Detection System for Enterprise Agentic AI Security](https://arxiv.org/abs/2605.17380)** (MLSys 2026).  
**Code:** [github.com/uber/ADR](https://github.com/uber/ADR)

ADR secures AI agents that use the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). This repository contains the open-source **ADR Sensor** (telemetry) and **ADR Detector** (benchmark + detection framework) described in the paper. The offline **ADR Explorer** red-teaming engine (§3) is not included here.

## Repository layout


| Path                                                 | Paper role               | Description                                                                          |
| ---------------------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------ |
| [Detection/](Detection/)                             | ADR Detector + ADR-Bench | Dual-agent detector, 133 MCP servers, 303 benchmark tasks, baselines, figure scripts |
| [Sensor/](Sensor/)                                   | ADR Sensor (§3.1)        | Collect and normalize agent telemetry from Claude Code, Cursor, Codex, and others    |
| [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)   | §5 evaluation            | Step-by-step workflow to reproduce benchmark detection and paper figures             |
| [CITATION.cff](CITATION.cff)                         | —                        | Citation metadata for the paper                                                      |


## Quick start

```bash
git clone https://github.com/uber/ADR
cd ADR/Detection
uv sync
export ANTHROPIC_API_KEY="..." OPENAI_API_KEY="..."
```

Default detector is `adr` (ADR dual-agent). For keyless smoke tests, use `--detector llamafirewall` (see [Detection/README.md](Detection/README.md)).

See **[docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)** for the full evaluation workflow (inflate packed benchmark → run detectors → plot figures).

Component documentation:

- [Detection/README.md](Detection/README.md) — ADR-Bench, detector baselines, MCP infrastructure
- [Sensor/README.md](Sensor/README.md) — telemetry collection and unified schema

## Citation

```bibtex
@article{li2026adr,
  title={ADR: An Agentic Detection System for Enterprise Agentic AI Security},
  author={Li, Chenning and Hu, Pan and Xu, Justin and Ozbas, Baris and Liu, Olivia and Van, Caroline and Li, Manxue and Zhou, Wei and Alizadeh, Mohammad and Zhang, Pengyu and Sriramadhesikan, KK and Zhang, Ming},
  journal={arXiv preprint arXiv:2605.17380},
  year={2026}
}
```

Or use [CITATION.cff](CITATION.cff).

## License

Apache License 2.0. See [LICENSE](LICENSE). `Detection/benchmark/agentdojo/` is vendored third-party code under its own [LICENSE](Detection/benchmark/agentdojo/LICENSE) (MIT).

## Data notice

`Detection/` includes **synthetic** benchmark fixtures (fake credentials, emulated environments, prompt-injection scenarios) for defensive security research only. Details: [docs/OPEN_SOURCE_REVIEW.md](docs/OPEN_SOURCE_REVIEW.md).