output "docker_network_name" {
  value = docker_network.app_network.name
}

output "docker_container_name" {
  value = docker_container.mongo.name
}

output "app_container_name" {
  value = docker_container.app.name
}

output "nginx_container_name" {
  value = docker_container.nginx.name
}

output "application_url" {
  value = "http://localhost:8080"
}