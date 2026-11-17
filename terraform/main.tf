terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~>3.6"
    }
  }
}

provider "docker" {}


resource "docker_network" "app_network" {
  name = "url_shortener_tf_network"
}

resource "docker_volume" "mongo_data" {
  name = "url_shortener_tf_mongo_data"
}

resource "docker_image" "mongo" {
  name = "mongo:7"
}

resource "docker_container" "mongo" {
  name  = "url_shortener_tf_mongo"
  image = docker_image.mongo.image_id

  restart = "unless-stopped"

  networks_advanced {
    name    = docker_network.app_network.name
    aliases = ["mongo"]
  }

  volumes {
    volume_name    = docker_volume.mongo_data.name
    container_path = "/data/db"
  }

  env = [
    "MONGO_INITDB_ROOT_USERNAME=${var.mongo_user}",
    "MONGO_INITDB_ROOT_PASSWORD=${var.mongo_password}"
  ]
}

resource "docker_image" "app" {
  name         = "ghcr.io/idhika22/url-shortener:latest"
  keep_locally = true
}

resource "docker_container" "app" {
  name  = "url_shortener_tf_app"
  image = docker_image.app.image_id

  restart = "unless-stopped"

  networks_advanced {
    name    = docker_network.app_network.name
    aliases = ["app"]
  }

  env = [
    "MONGODB_URI=mongodb://${var.mongo_user}:${var.mongo_password}@mongo:27017/?authSource=admin",
    "MONGO_DB=${var.mongo_db}"
  ]

  depends_on = [
    docker_container.mongo
  ]
}

resource "docker_image" "nginx" {
  name         = "nginx:1.27-alpine"
  keep_locally = true
}

resource "docker_container" "nginx" {
  name  = "url_shortener_tf_nginx"
  image = docker_image.nginx.image_id

  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.app_network.name
  }

  ports {
    internal = 80
    external = 8080
  }

  volumes {
    host_path      = abspath("${path.module}/../nginx/default.conf")
    container_path = "/etc/nginx/conf.d/default.conf"
    read_only      = true
  }

  depends_on = [
    docker_container.app
  ]
}