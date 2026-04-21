🚀 Lecture 10: Nomad + Ollama (AI Workloads on Nomad)

📌 Overview

This project demonstrates how to run AI workloads using HashiCorp Nomad by deploying Ollama and dynamically pulling LLM models via API.

It follows:

Lecture 9 → Nomad job scheduling

Lecture 8 → Cloud scalability concepts

⚙️ Tech Stack

🧠 Ollama (LLM runtime)

☁️ HashiCorp Nomad

🐧 raw_exec driver (macOS compatible)

🌐 cURL API

🖥️ Open WebUI (optional)

🚀 Features

Nomad job orchestration

Poststart lifecycle hook

Multi-model support

API-based verification

macOS-compatible setup

Lightweight resource usage

📂 Project Structure

lecture10/
│
├── assignment/
│ ├── ollama.nomad.hcl
│ └── open-webui.nomad.hcl
│
├── assignment_submission/
│ ├── README.md
│ ├── SHORT_NOTE.md
│ ├── JOBSPEC_CHANGES.md
│ ├── PR_BODY.md
│ ├── api-tags-output.json
│ └── screenshots/

🛠️ Setup Instructions

1️⃣ Start Nomad

nomad agent -dev
2️⃣ Start Ollama

/opt/homebrew/bin/ollama serve
3️⃣ Run the Job

nomad job run assignment/ollama.nomad.hcl
🔍 Verify Deployment

curl http://localhost:11434/api/tags
✅ Expected Output

{
"models": [
    { "name": "tinyllama" },
    { "name": "qwen:0.5b" }
]
}

🤖 Models Used

Model        Description

tinyllama   Lightweight testing

qwen:0.5b   Better responses 

🎯 Key Concepts

Nomad job scheduling

Task groups & lifecycle hooks

Poststart execution

AI workload orchestration

Resource optimization

⚠️ Challenges & Fixes

Issue                               Solution

Docker driver not working (macOS)   Used raw_exec

exec driver unsupported             Switched to raw_exec

Consul error                        Removed service block

CPU exhaustion                      Reduced resources

PATH issues                         Used absolute paths


🧠 Architecture

User / API Request
↓
Nomad Scheduler (Job)
↓
Task Group
├── Ollama Server (raw_exec)
└── Poststart Task (Model Pull)
↓
Ollama API (/api/pull)
↓
Models Loaded (tinyllama, qwen)
↓
Verification (/api/tags)
↓
(Optional) Open WebUI (Frontend)

🌐 Optional: Open WebUI

Run:

docker run -d --name open-webui \
-p 3000:3000 \
-e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
ghcr.io/open-webui/open-webui:main

Open:

👉 http://localhost:3000

📸 Screenshots

Nomad UI (running job)

API /api/tags output

Open WebUI (bonus)

🎤 Viva Highlights

Why raw_exec?

macOS does not support exec/docker drivers reliably

What is poststart?

Runs after main service starts

Why sleep?

Ensures service readiness

Why no Consul?

Not required for local dev

👨‍💻 Author

Subhankar Biswas

⭐ Final Result

✔ Nomad Job Running

✔ Ollama Deployed

✔ Models Pulled

✔ API Verified

✔ UI (Optional) Working
