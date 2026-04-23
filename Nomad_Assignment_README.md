## 🚀 Lecture 9: Nomad Hello World - Subhankar Biswas

### 📌 Overview

This PR demonstrates a minimal batch job execution using **HashiCorp Nomad**. The assignment validates the setup of a local Nomad development cluster and successful execution of a containerized task using Docker.

---

### 🎯 Objectives Completed

* Installed and verified Nomad CLI (≥ 1.5)
* Started a local Nomad development agent
* Configured Nomad client with Docker driver
* Submitted a batch job (`hello-world.nomad.hcl`)
* Verified successful job execution
* Retrieved logs from allocation output
* Cleaned up job resources

---

### ⚙️ Implementation Details

#### 🧩 Job Type

* **Type:** Batch job
* **Purpose:** Execute a one-time task and terminate

#### 🐳 Task Runtime

* **Driver:** Docker
* **Image:** busybox
* **Command:**

  ```bash
  echo "Hello, world from Nomad!"
  ```

#### 💻 Resource Allocation

* CPU: 1 MHz (minimum Nomad unit)
* Memory: 64 MB

---

### ▶️ How to Run

```bash
# Start Nomad agent
nomad agent -dev -data-dir=$HOME/nomad-dev-data

# Run job
nomad job run assignment/hello-world.nomad.hcl

# Check job status
nomad job status hello-world

# View logs
nomad alloc logs <allocation-id> hello
```

---

### ✅ Expected Output

```bash
Hello, world from Nomad!
```

---

### 🖥️ UI Verification

Nomad UI: http://localhost:4646

* Job: `hello-world`
* Status: **Complete**
* Logs: Display expected output

---

### 🧹 Cleanup

```bash
nomad job stop -purge hello-world
```

---

### 📸 Submission Artifacts

* Screenshot of Nomad UI OR terminal logs
* Job specification file included

---

### 💡 Key Learnings

* Basics of job scheduling in Nomad
* Difference between batch and service jobs
* Docker integration with Nomad
* Resource allocation and scheduling constraints

---

### 🔮 Optional Extension

* Deploy nginx service using Nomad
* Expose port 8080 for browser access

---

### 📚 References

* Nomad Official Documentation
* Lecture 9 Notes
