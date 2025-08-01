from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Check and show user roles and groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Check specific username',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            try:
                user = User.objects.get(username=username)
                self.show_user_info(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" does not exist.')
                )
        else:
            # Show all users
            users = User.objects.prefetch_related('groups').all()
            for user in users:
                self.show_user_info(user)
                self.stdout.write("-" * 50)

    def show_user_info(self, user):
        self.stdout.write(f"Username: {user.username}")
        self.stdout.write(f"Email: {user.email}")
        self.stdout.write(f"Is Active: {user.is_active}")
        self.stdout.write(f"Is Superuser: {user.is_superuser}")
        self.stdout.write(f"Is Staff: {user.is_staff}")
        
        groups = user.groups.all()
        if groups:
            group_names = [group.name for group in groups]
            self.stdout.write(f"Groups: {', '.join(group_names)}")
        else:
            self.stdout.write("Groups: None")
        
        # Check permissions
        if user.groups.filter(name='admin').exists():
            self.stdout.write(self.style.SUCCESS("Has admin role"))
        elif user.groups.filter(name='agent').exists():
            self.stdout.write(self.style.SUCCESS("Has agent role"))
        else:
            self.stdout.write(self.style.WARNING("No admin or agent role"))