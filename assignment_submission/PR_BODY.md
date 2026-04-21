# PR Title
Lecture 10: Nomad + Ollama - Subhankar Biswas

---

# Summary
Completed Nomad + Ollama assignment with working multi-model setup.

---

# Implementation
- Ollama deployed via Nomad
- Models pulled using poststart task
- Models used:
- tinyllama
- qwen:0.5b

---

# Screenshots
- Nomad UI running job
- API tags output
- WebUI

---

# Challenges Solved
- Docker driver not supported on macOS
- Used raw_exec driver instead
- Fixed CPU resource constraints
- Removed Consul dependency

---

# Result
Successful deployment and verification of AI workload using Nomad.