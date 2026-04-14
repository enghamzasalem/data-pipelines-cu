# Lecture 10: Nomad + Ollama

Theme: run a private local LLM workload on Nomad using Ollama, with the same service plus poststart model-pull idea used in the official AI workloads tutorial.

## Assignment

Available jobspecs:

- `assignment/ollama.nomad.hcl` for Docker
- `assignment/ollama-windows.nomad.hcl` for Windows without Docker
- `assignment/open-webui.nomad.hcl` for the optional bonus UI

See `LECTURE10_ASSIGNMENT_README.md` for the submission steps.

## Prerequisites

- Nomad >= 1.5
- Docker for the Docker path
- On Windows without Docker, use `nomad-dev-windows.hcl` and the Windows jobspec

## Reference

- [AI workloads on Nomad - Overview](https://developer.hashicorp.com/nomad/tutorials/ai-workloads/ai-workloads-overview)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
