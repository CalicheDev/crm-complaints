from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction


class Command(BaseCommand):
    help = 'Setup initial data: groups and admin user'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username for admin user (default: admin)'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@example.com',
            help='Email for admin user (default: admin@example.com)'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Password for admin user (default: admin123)'
        )
    
    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Create groups
                admin_group, created = Group.objects.get_or_create(name='admin')
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('Created admin group')
                    )
                else:
                    self.stdout.write('Admin group already exists')
                
                agent_group, created = Group.objects.get_or_create(name='agent')
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('Created agent group')
                    )
                else:
                    self.stdout.write('Agent group already exists')
                
                # Create admin user
                admin_username = options['admin_username']
                admin_email = options['admin_email']
                admin_password = options['admin_password']
                
                if not User.objects.filter(username=admin_username).exists():
                    admin_user = User.objects.create_user(
                        username=admin_username,
                        email=admin_email,
                        password=admin_password,
                        first_name='System',
                        last_name='Administrator',
                        is_staff=True,
                        is_superuser=True
                    )
                    admin_user.groups.add(admin_group)
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created admin user: {admin_username}'
                        )
                    )
                    self.stdout.write(
                        f'Admin credentials: {admin_username} / {admin_password}'
                    )
                else:
                    self.stdout.write('Admin user already exists')
                
                self.stdout.write(
                    self.style.SUCCESS('Initial data setup completed successfully!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up initial data: {str(e)}')
            )