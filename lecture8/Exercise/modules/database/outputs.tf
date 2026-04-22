output "db_endpoint" {
  value = var.create_database ? aws_db_instance.main[0].endpoint : null
}

output "db_address" {
  value = var.create_database ? aws_db_instance.main[0].address : null
}
