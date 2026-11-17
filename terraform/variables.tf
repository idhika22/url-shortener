
variable "mongo_user" {
  description = "MongoDB root username"
  type        = string
  sensitive   = true
}

variable "mongo_password" {
  description = "MongoDB root password"
  type        = string
  sensitive   = true
}

variable "mongo_db" {
  description = "MongoDB database name"
  type        = string
  default     = "shortener"
}
