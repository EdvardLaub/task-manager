from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.tasks import generate_task_report

class Command(BaseCommand):
    help = 'Send daily task reports to all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Send report to specific user ID',
        )
        parser.add_argument(
            '--report-type',
            type=str,
            default='daily',
            help='Type of report (daily, weekly, monthly)',
        )

    def handle(self, *args, **options):
        if options['user_id']:
            users = User.objects.filter(id=options['user_id'])
        else:
            users = User.objects.filter(is_active=True, email__isnull=False)

        for user in users:
            generate_task_report.delay(user.id, options['report_type'])
            self.stdout.write(
                self.style.SUCCESS(f'Queued report for user: {user.username}')
            )