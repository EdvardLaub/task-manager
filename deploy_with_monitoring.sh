#!/bin/bash
# Simple deployment script with monitoring

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not activated. Activating..."
    source venv/bin/activate
fi

print_status "Starting deployment with monitoring setup..."

# Step 1: Deploy application
print_status "Step 1: Deploying application..."
ansible-playbook deploy.yml -v

# Step 2: Set up monitoring
print_status "Step 2: Setting up monitoring..."
ansible-playbook monitoring.yml -v

# Step 3: Run health check
print_status "Step 3: Running health check..."
ansible-playbook health_monitoring.yml

# Step 4: Test backup
print_status "Step 4: Testing backup system..."
ansible webservers -m shell -a "/usr/local/bin/backup_task_manager.sh" --become

# Step 5: Display summary
print_status "Step 5: Deployment Summary"
echo "================================="
echo "✅ Application: Deployed"
echo "✅ Monitoring: Configured"
echo "✅ Backup: Tested"
echo "✅ Health Check: Completed"
echo ""
echo "🌐 Application URL: http://64.226.111.192"
echo "🔐 SSH Access: ssh -i ~/.ssh/digitalocean_key root@64.226.111.192"
echo ""
echo "📊 To check application status:"
echo "   ansible-playbook health_monitoring.yml"
echo ""
echo "💾 To run manual backup:"
echo "   ansible webservers -m shell -a '/usr/local/bin/backup_task_manager.sh' --become"

print_status "Deployment completed successfully!"
