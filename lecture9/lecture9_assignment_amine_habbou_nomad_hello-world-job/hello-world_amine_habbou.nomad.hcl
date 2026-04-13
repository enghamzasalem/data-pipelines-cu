job "hello-world" {
  datacenters = ["dc1"]
  type = "batch"

  group "app" {
    task "hello" {
      driver = "raw_exec"

      config {
        command = "cmd.exe"
        args = ["/c", "echo Hello world from Nomad! it's Amine"]
      }

      resources {
        cpu    = 1
        memory = 64
      }
    }
  }
}