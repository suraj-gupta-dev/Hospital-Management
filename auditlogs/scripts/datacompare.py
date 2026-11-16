from django.contrib.auth import get_user_model

User = get_user_model()

def run():
    first_user = User.objects.values().first()
    last_user = User.objects.values().last()

    print(set(first_user) | set(last_user))