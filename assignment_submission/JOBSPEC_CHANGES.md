# Jobspec Changes (macOS-Based Submission)

This submission required modifications due to macOS limitations and Nomad dev cluster constraints.

---

## 1. assignment/ollama.nomad.hcl

### 🔁 Model Change
- Replaced default model:
- ❌ `tinyllama`
- ✅ `qwen:0.5b`

- Reason:
- Lightweight and suitable for low-resource environments
- Faster download and execution on local machine

---

### ⚙️ Resource Optimization
- Reduced resources to fit Nomad dev agent limits:

| Task | CPU | Memory |
|--------------|-----|--------|
| ollama-task | 10 | 512 MB |
| pull-model | 5 | 128 MB |

- Reason:
- Nomad dev mode provides very limited CPU capacity (~28 MHz)
- Higher values caused:
```
Dimension "cpu" exhausted
```

---

### 🖥️ Driver Fix (macOS Compatibility)
- Replaced:
- ❌ `exec`
- ❌ `docker`
- ✅ `raw_exec`

- Reason:
- `exec` driver is unsupported on macOS
- `docker` driver not detected in local setup
- `raw_exec` is the only stable option

---

### 📍 Absolute Path Fix
- Used full binary path for Ollama:

/opt/homebrew/bin/ollama

- Reason:
- `raw_exec` does not inherit system PATH
- Prevents `command not found` errors

---

### ⏱️ Startup Synchronization
- Added delay before pulling models:

sleep 10

- Reason:
- Ensures Ollama server is fully started before API calls

---

### 🌐 Consul Dependency Removed
- Removed `service` block

- Reason:
- Service registration requires Consul
- Caused error:
```
Constraint "${attr.consul.version}"
```

---

## 2. assignment/open-webui.nomad.hcl

### 🔄 Execution Strategy
- Used `raw_exec` instead of Docker driver

- Reason:
- Docker driver not supported reliably on macOS Nomad client

---

### 🔗 Backend Connection
- Set:
OLLAMA_BASE_URL=http://localhost:11434

- Reason:
- Connect Open WebUI to locally running Ollama

---

### ⚙️ Runtime Setup
- Installed Open WebUI dynamically:
pip install open-webui

- Reason:
- Avoid dependency issues
- Ensure portability

---

## ⚠️ Key macOS Constraints

- `exec` driver → ❌ unsupported
- `docker` driver → ❌ unreliable
- `raw_exec` → ✅ required

---

## 🧠 Summary

These changes ensure:
- macOS compatibility
- Stable execution in Nomad dev environment
- Efficient resource usage
- Successful model deployment

---

## 🎯 Outcome

✔ Nomad job successfully scheduled
✔ Ollama server running
✔ Model `qwen:0.5b` pulled
✔ API verified via `/api/tags`
✔ Open WebUI connected

---