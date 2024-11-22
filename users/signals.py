from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    roles = ['admin', 'agent', 'client']
    for role in roles:
        Group.objects.get_or_create(name=role)