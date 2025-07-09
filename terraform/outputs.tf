output "droplet_ip" {
  value = "64.226.111.192"
  description = "IP address of the droplet"
}

output "tag_name" {
  value = digitalocean_tag.task_manager_tag.name
  description = "Name of the created tag"
}

output "domain_name" {
  value = var.domain_name != "" ? var.domain_name : "Not configured"
  description = "Configured domain name"
}

output "ssh_connection" {
  value = "ssh -i ~/.ssh/digitalocean_key root@64.226.111.192"
  description = "SSH connection command"
}

output "firewall_id" {
  value = var.droplet_id != "" ? digitalocean_firewall.task_manager_firewall[0].id : "Not created"
  description = "ID of the firewall"
}
