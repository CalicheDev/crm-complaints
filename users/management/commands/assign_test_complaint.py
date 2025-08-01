from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from complaints.models import Complaint


class Command(BaseCommand):
    help = 'Assign a test complaint to an agent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--complaint-id',
            type=int,
            help='ID of the complaint to assign',
            required=True
        )
        parser.add_argument(
            '--agent-username',
            type=str,
            help='Username of the agent to assign the complaint to',
            required=True
        )

    def handle(self, *args, **options):
        complaint_id = options['complaint_id']
        agent_username = options['agent_username']
        
        try:
            complaint = Complaint.objects.get(id=complaint_id)
            agent = User.objects.get(username=agent_username)
            
            # Verify agent has agent role
            if not agent.groups.filter(name='agent').exists():
                self.stdout.write(
                    self.style.ERROR(f'User "{agent_username}" is not an agent.')
                )
                return
            
            # Assign complaint to agent
            complaint.assigned_to = agent
            complaint.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned complaint "{complaint.title}" (ID: {complaint_id}) to agent "{agent_username}"'
                )
            )
            
        except Complaint.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Complaint with ID {complaint_id} does not exist.')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{agent_username}" does not exist.')
            )