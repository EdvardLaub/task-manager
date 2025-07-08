import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, Category, Tag, Team, TaskAttachment

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            user=self.user
        )
        
    def test_task_creation(self):
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            user=self.user,
            category=self.category
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 'medium')
        
    def test_task_is_overdue(self):
        past_date = timezone.now() - timedelta(days=1)
        task = Task.objects.create(
            title='Overdue Task',
            user=self.user,
            due_date=past_date,
            status='pending'
        )
        self.assertTrue(task.is_overdue)
        
    def test_task_has_reminder(self):
        past_date = timezone.now() - timedelta(hours=1)
        task = Task.objects.create(
            title='Reminder Task',
            user=self.user,
            reminder_date=past_date,
            status='pending'
        )
        self.assertTrue(task.has_reminder)