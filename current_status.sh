#!/bin/bash
# Check current application status

source venv/bin/activate

echo "🔍 Current Application Status"
echo "============================"

echo "1. Testing application response..."
curl -I http://64.226.111.192

echo ""
echo "2. What's running on the server..."
ansible webservers -m shell -a "ps aux | grep -E '(python|flask|gunicorn|nginx)' | grep -v grep" --become

echo ""
echo "3. What's listening on ports..."
ansible webservers -m shell -a "ss -tlnp | grep -E ':(80|5000|8000)'" --become

echo ""
echo "4. Nginx status..."
ansible webservers -m shell -a "systemctl status nginx" --become

echo ""
echo "5. Supervisor status..."
ansible webservers -m shell -a "supervisorctl status" --become

echo ""
echo "6. Check if Docker is installed..."
ansible webservers -m shell -a "which docker" --become

echo ""
echo "✅ Current status check completed!"
EOF

chmod +x current_status.sh

# Run the current status check
./current_status.sh