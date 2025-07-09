terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# Configure the DigitalOcean Provider
provider "digitalocean" {
  token = var.do_token
}

# Create a tag to test the connection
resource "digitalocean_tag" "task_manager_tag" {
  name = "task-manager-terraform"
}

# Optional: Create a domain resource if you have a domain
resource "digitalocean_domain" "task_manager_domain" {
  count = var.domain_name != "" ? 1 : 0
  
  name = var.domain_name
  ip_address = "64.226.111.192"
}

# Optional: Create A record for www
resource "digitalocean_record" "www" {
  count = var.domain_name != "" ? 1 : 0
  
  domain = digitalocean_domain.task_manager_domain[0].name
  type   = "A"
  name   = "www"
  value  = "64.226.111.192"
}
resource "digitalocean_firewall" "task_manager_firewall" {
  count = var.droplet_id != "" ? 1 : 0
  
  name = "task-manager-firewall"
  
  droplet_ids = [var.droplet_id]
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
