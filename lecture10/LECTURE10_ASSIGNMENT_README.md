# Lecture 10: Nomad + Ollama Assignment

Run Ollama on Nomad and pull a small model using the same Nomad pattern as the AI workloads tutorial: a service task plus a poststart task that calls `/api/pull`.

## Objectives

1. Start a Nomad dev cluster.
2. Submit the Ollama job.
3. Verify the model pull.
4. Call `http://localhost:11434/api/tags` to show the installed model.
5. Optional bonus: run Open WebUI after Ollama is healthy.

## Prerequisites

- Nomad CLI
- Enough RAM for a small local model
- On Windows without Docker, use `assignment/ollama-windows.nomad.hcl`
- If Docker is available, you may still use `assignment/ollama.nomad.hcl`

## Recommended path on this laptop

Windows without Docker:

```powershell
nomad agent -dev -bind 127.0.0.1 -data-dir="$PWD/.nomad-dev-data" -config=nomad-dev-windows.hcl
```

In another terminal:

```powershell
$env:NOMAD_ADDR = "http://127.0.0.1:4646"
nomad job run assignment/ollama-windows.nomad.hcl
```

## Verify the model

Wait for the `pull-model` task to finish, then run:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:11434/api/tags"
```

## Optional bonus

If Docker is available and the machine has enough RAM, run:

```bash
nomad job run assignment/open-webui.nomad.hcl
```

## How to submit

1. Screenshot of Nomad UI showing job `ollama` running.
2. Screenshot of `api/tags` output in the terminal.
3. Short note linking the work back to Lecture 8 or Lecture 9.
4. Pull request with screenshots and any jobspec changes.

### PR title example

```text
Lecture 10: Nomad + Ollama - [Your Name]
```
