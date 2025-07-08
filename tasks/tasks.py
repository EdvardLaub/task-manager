from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Task, TaskHistory
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_reminder_emails():
    """Send reminder emails for tasks that have reached their reminder date"""
    tasks_with_reminders = Task.objects.filter(
        reminder_date__lte=timezone.now(),
        reminder_sent=False,
        status__in=['pending', 'in_progress']
    ).select_related('user', 'assigned_to')
    
    emails = []
    tasks_updated = []
    
    for task in tasks_with_reminders:
        recipient = task.assigned_to or task.user
        
        if recipient.email:
            subject = f"Task Reminder: {task.title}"
            
            # Render HTML email template
            html_message = render_to_string('emails/task_reminder.html', {
                'task': task,
                'recipient': recipient,
                'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'
            })
            
            # Plain text version
            plain_message = f"""
            Hi {recipient.first_name or recipient.username},
            
            This is a reminder for your task: {task.title}
            
            Description: {task.description}
            Priority: {task.get_priority_display()}
            Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}
            
            Please complete this task as soon as possible.
            
            Best regards,
            Task Manager Team
            """
            
            emails.append((
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email]
            ))
            
            tasks_updated.append(task)
    
    if emails:
        try:
            send_mass_mail(emails, fail_silently=False)
            
            # Mark reminders as sent
            for task in tasks_updated:
                task.reminder_sent = True
                task.save()
                
                # Create history entry
                TaskHistory.objects.create(
                    task=task,
                    user=task.user,
                    action='reminder_sent',
                    details=f'Reminder email sent to {task.assigned_to.email if task.assigned_to else task.user.email}'
                )
            
            logger.info(f'Sent {len(emails)} reminder emails')
            return f'Sent {len(emails)} reminder emails'
            
        except Exception as e:
            logger.error(f'Failed to send reminder emails: {e}')
            return f'Failed to send reminder emails: {e}'
    
    return 'No reminder emails to send'

@shared_task
def send_task_assignment_email(task_id, assigned_by_id):
    """Send email when a task is assigned to a user"""
    try:
        task = Task.objects.get(id=task_id)
        assigned_by = task.user
        
        if task.assigned_to and task.assigned_to.email:
            subject = f"New Task Assigned: {task.title}"
            
            html_message = render_to_string('emails/task_assignment.html', {
                'task': task,
                'assigned_by': assigned_by,
                'assigned_to': task.assigned_to,
                'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'
            })
            
            plain_message = f"""
            Hi {task.assigned_to.first_name or task.assigned_to.username},
            
            You have been assigned a new task: {task.title}
            
            Assigned by: {assigned_by.first_name or assigned_by.username}
            Description: {task.description}
            Priority: {task.get_priority_display()}
            Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}
            
            Please review and complete this task.
            
            Best regards,
            Task Manager Team
            """
            
            from django.core.mail import send_mail
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [task.assigned_to.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return f'Assignment email sent for task: {task.title}'
            
    except Task.DoesNotExist:
        return 'Task not found'
    except Exception as e:
        logger.error(f'Failed to send assignment email: {e}')
        return f'Failed to send assignment email: {e}'

@shared_task
def generate_task_report(user_id, report_type='weekly'):
    """Generate and send task reports"""
    from django.contrib.auth.models import User
    from datetime import datetime, timedelta
    
    try:
        user = User.objects.get(id=user_id)
        
        # Calculate date range
        end_date = timezone.now()
        if report_type == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Get tasks for the period
        tasks = Task.objects.filter(
            user=user,
            created_at__range=[start_date, end_date]
        ).select_related('category').prefetch_related('tags')
        
        # Generate statistics
        stats = {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='completed').count(),
            'overdue_tasks': tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count(),
            'high_priority_tasks': tasks.filter(priority='high').count(),
        }
        
        if user.email:
            subject = f"Task Report - {report_type.title()}"
            
            html_message = render_to_string('emails/task_report.html', {
                'user': user,
                'tasks': tasks,
                'stats': stats,
                'report_type': report_type,
                'start_date': start_date,
                'end_date': end_date,
            })
            
            from django.core.mail import send_mail
            send_mail(
                subject,
                f"Your {report_type} task report is ready. Please view the HTML version for details.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return f'Report sent to {user.email}'
        
    except User.DoesNotExist:
        return 'User not found'
    except Exception as e:
        logger.error(f'Failed to generate report: {e}')
        return f'Failed to generate report: {e}'