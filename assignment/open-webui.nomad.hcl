job "open-webui" {
  datacenters = ["dc1"]

  group "webui-group" {

    network {
      port "http" {
        static = 3000
      }
    }

    task "webui" {
      driver = "raw_exec"

      config {
        command = "/bin/sh"
        args = [
          "-c",
          <<EOF
pip install open-webui && \
export OLLAMA_BASE_URL=http://localhost:11434 && \
open-webui serve --host 127.0.0.1 --port 3000
EOF
        ]
      }

      resources {
        cpu    = 10
        memory = 512
      }
    }
  }
}