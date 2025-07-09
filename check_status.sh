#!/bin/bash
# Quick status check

source venv/bin/activate

echo "🔍 Quick Status Check"
echo "===================="

# Test application
echo "📱 Application Status:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://64.226.111.192

# Check services
echo ""
echo "🛠️ Services Status:"
ansible webservers -m shell -a "systemctl is-active nginx postgresql supervisor" --become

# Check disk space
echo ""
echo "💾 Disk Usage:"
ansible webservers -m shell -a "df -h /var/www" --become

# Check backup status
echo ""
echo "🔐 Backup Status:"
ansible webservers -m shell -a "ls -la /var/backups/task-manager/ 2>/dev/null | tail -3 || echo 'No backups found'" --become

# Check fail2ban status
echo ""
echo "🔒 Security Status:"
ansible webservers -m shell -a "fail2ban-client status sshd 2>/dev/null || echo 'fail2ban not configured'" --become

echo ""
echo "✅ Status check completed!"