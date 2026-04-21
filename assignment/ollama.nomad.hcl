job "ollama" {
  datacenters = ["dc1"]

  group "ollama-group" {

    network {
      port "http" {
        static = 11434
      }
    }


    # 🔹 Task 1: Run Ollama server locally
    task "ollama" {
      driver = "raw_exec"

      config {
        command = "/opt/homebrew/bin/ollama"
        args    = ["serve"]
      }

      resources {
        cpu    = 10
        memory = 512
      }
    }

    # 🔹 Task 2: Pull models after server starts
    task "pull-model" {
      driver = "raw_exec"

      lifecycle {
        hook = "poststart"
      }

      config {
        command = "/bin/sh"
        args = [
          "-c",
          <<EOF
sleep 5 && \
curl -X POST http://localhost:11434/api/pull -d '{"name":"tinyllama"}' && \
curl -X POST http://localhost:11434/api/pull -d '{"name":"qwen:0.5b"}'
EOF
        ]
      }

      resources {
        cpu    = 5
        memory = 128
      }
    }
  }
}