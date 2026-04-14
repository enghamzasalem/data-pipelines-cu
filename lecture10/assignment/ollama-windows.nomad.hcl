job "ollama" {
  type = "service"

  group "ollama" {
    count = 1

    network {
      port "ollama" {
        to     = 11434
        static = 11434
      }
    }

    task "ollama-task" {
      driver = "raw_exec"

      service {
        name     = "ollama-backend"
        port     = "ollama"
        provider = "nomad"
      }

      env {
        OLLAMA_HOST = "0.0.0.0:11434"
      }

      config {
        command = "C:/Users/ASUS/AppData/Local/Microsoft/WinGet/Packages/Ollama.Ollama.Portable_Microsoft.Winget.Source_8wekyb3d8bbwe/ollama.exe"
        args    = ["serve"]
      }

      resources {
        cpu    = 1000
        memory = 3072
      }
    }

    task "pull-model" {
      driver = "raw_exec"

      lifecycle {
        hook    = "poststart"
        sidecar = false
      }

      resources {
        cpu    = 50
        memory = 256
      }

      template {
        data = <<EOH
OLLAMA_BASE_URL=http://127.0.0.1:11434
EOH
        destination = "secrets/env.env"
        env         = true
      }

      template {
        data = <<EOH
{"name":"tinyllama"}
EOH
        destination = "local/pull.json"
      }

      config {
        command = "powershell.exe"
        args = [
          "-NoProfile",
          "-Command",
          <<-PS1
$ErrorActionPreference = "Stop"
Write-Output "Waiting for Ollama at http://127.0.0.1:11434 ..."
for ($i = 0; $i -lt 90; $i++) {
  try {
    curl.exe -sS "http://127.0.0.1:11434/api/tags" | Out-Null
    break
  } catch {
    Start-Sleep -Seconds 2
  }
}
Write-Output "Pulling tinyllama ..."
curl.exe -sS -X POST "http://127.0.0.1:11434/api/pull" --data-binary "@local/pull.json"
Write-Output "Done."
PS1
        ]
      }
    }
  }
}
