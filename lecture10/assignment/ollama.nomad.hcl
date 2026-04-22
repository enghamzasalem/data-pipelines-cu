job "ollama" {
  datacenters = ["dc1"]

  group "ollama-group" {

    task "ollama-task" {
      driver = "raw_exec"

      config {
        command = "cmd.exe"
        args = [
          "/c",
          "start /B C:\\Users\\joshi\\AppData\\Local\\Programs\\Ollama\\ollama.exe serve"
        ]
      }

      resources {
        cpu    = 500
        memory = 512
      }
    }
  }
}