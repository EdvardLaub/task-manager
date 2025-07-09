variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Domain name for the application (optional)"
  type        = string
  default     = ""
}

variable "droplet_id" {
  description = "ID of the existing droplet"
  type        = string
  default     = ""
}
