from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class Command(BaseCommand):
    help = "Creating Token for every user."

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            Token.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS("Successfully Token Assign to all Users."))