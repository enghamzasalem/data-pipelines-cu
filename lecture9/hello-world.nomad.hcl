job "hello-world" {
  datacenters = ["dc1"]

  group "example" {
    task "hello" {
      driver = "raw_exec"

      config {
        command = "cmd.exe"
        args = ["/c", "ping -t 127.0.0.1"]
      }
    }
  }
}