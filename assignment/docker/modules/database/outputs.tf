output "connection_string" {
  value = "postgresql://${var.db_user}:${var.db_password}@localhost:5432/${var.db_name}"
}