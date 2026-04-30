output "webserver_url" {
  value = "http://${aws_instance.web.public_ip}:8080"
}

output "n8n_url" {
  value = "http://${aws_instance.web.public_ip}:5678"
}