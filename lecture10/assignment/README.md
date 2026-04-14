# Lecture 10 assignment jobspecs

| File | Purpose |
|------|---------|
| `ollama.nomad.hcl` | Docker-based Ollama job with a poststart model pull |
| `ollama-windows.nomad.hcl` | Windows no-Docker Ollama job using `raw_exec` |
| `open-webui.nomad.hcl` | Optional UI that depends on Ollama |

Basic Nomad command:

```bash
nomad job run assignment/ollama.nomad.hcl
```

Windows alternative:

```powershell
nomad job run assignment/ollama-windows.nomad.hcl
```

See `../LECTURE10_ASSIGNMENT_README.md` for the full assignment workflow.
