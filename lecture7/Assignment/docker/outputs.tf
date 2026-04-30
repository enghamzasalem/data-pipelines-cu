output "webserver_url" {
  description = "URL of the web server landing page"
  value       = "http://localhost:8080"
}

output "n8n_url" {
  description = "URL of the n8n workflow automation UI"
  value       = "http://localhost:5678"
}

output "dependency_note" {
  description = "Reminder about the startup order"
  value       = "Webserver started first → n8n started after (depends_on = [docker_container.webserver])"
}
