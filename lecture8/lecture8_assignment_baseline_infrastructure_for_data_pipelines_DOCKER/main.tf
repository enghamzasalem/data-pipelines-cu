# Create Docker network (no subnet to avoid conflicts)
resource "docker_network" "pipeline_network" {
  name = var.network_name
  driver = "bridge"
}

# Storage module
module "storage" {
  source = "./modules/storage"
  
  container_name = "${var.project_name}-${var.environment}-minio"
  root_user      = var.minio_root_user
  root_password  = var.minio_root_password
  network_name   = docker_network.pipeline_network.name
  
  depends_on = [docker_network.pipeline_network]
}

# Database module
module "database" {
  source = "./modules/database"
  
  container_name    = "${var.project_name}-${var.environment}-postgres"
  postgres_user     = var.postgres_user
  postgres_password = var.postgres_password
  postgres_db       = var.postgres_db
  network_name      = docker_network.pipeline_network.name
  
  depends_on = [docker_network.pipeline_network]
}

# Create buckets using null_resource with proper formatting
resource "null_resource" "create_buckets" {
  for_each = toset(var.buckets)
  
  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command = "sleep 10 && docker exec ${module.storage.container_name} mc alias set myminio http://localhost:9000 ${var.minio_root_user} ${var.minio_root_password} && docker exec ${module.storage.container_name} mc mb myminio/${var.project_name}-${var.environment}-${each.value} --ignore-existing"
  }
  
  depends_on = [module.storage]
}