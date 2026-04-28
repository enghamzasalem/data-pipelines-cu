data_dir  = "/Users/tlaytmass/data-pipelines-cu-7/lecture10/assignment/nomad-data"
plugin_dir = "/Users/tlaytmass/data-pipelines-cu-7/lecture10/assignment/plugins"

client {
  enabled = true
}

plugin "docker" {
  config {
    allow_privileged = true
  }
}
