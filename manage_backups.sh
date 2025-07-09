#!/bin/bash
# Backup management script

source venv/bin/activate

case "$1" in
    "create")
        echo "Creating backup..."
        ansible webservers -m shell -a "/usr/local/bin/simple_backup.sh" --become
        ;;
    "list")
        echo "Listing backups..."
        ansible webservers -m shell -a "ls -la /var/backups/task-manager/" --become
        ;;
    "clean")
        echo "Cleaning old backups..."
        ansible webservers -m shell -a "find /var/backups/task-manager -name '*.tar.gz' -mtime +7 -delete" --become
        ansible webservers -m shell -a "find /var/backups/task-manager -name '*.sql' -mtime +7 -delete" --become
        ;;
    "status")
        echo "Backup status..."
        ansible webservers -m shell -a "du -sh /var/backups/task-manager/ && echo 'Latest backups:' && ls -lt /var/backups/task-manager/ | head -5" --become
        ;;
    *)
        echo "Usage: $0 {create|list|clean|status}"
        echo "  create - Create a new backup"
        echo "  list   - List all backups"
        echo "  clean  - Clean old backups"
        echo "  status - Show backup status"
        ;;
esac