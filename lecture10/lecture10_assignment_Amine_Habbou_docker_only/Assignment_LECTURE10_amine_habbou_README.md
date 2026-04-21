# Lecture 10 - Ollama on WSL2

## What I did
- Ran Ollama with Docker on WSL2 (Nomad had CPU detection issues on WSL2)
- Pulled tinyllama model
- Added Open WebUI for chat interface

## Why not Nomad?
- Windows: Docker driver needs Windows containers (Ollama needs Linux)
- WSL2: Nomad CPU detection bug (shows 0/0 MHz)

## What works
- Ollama: http://localhost:11434
- Open WebUI: http://localhost:3000
- Model: tinyllama

## Commands
```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker exec ollama ollama pull tinyllama
docker run -d --name open-webui -p 3000:8080 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 ghcr.io/open-webui/open-webui:main