output "webserver_url" {
  description = "URL of the web server"
  value       = "http://${aws_instance.lecture7.public_ip}:8080"
}

output "n8n_url" {
  description = "URL of the n8n UI"
  value       = "http://${aws_instance.lecture7.public_ip}:5678"
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.lecture7.public_ip
}

output "dependency_note" {
  description = "Startup order in user_data"
  value       = "1. Docker installed → 2. Webserver started → 3. n8n started after webserver"
}
