from accounts.models import User

def run():
    users = User.objects.values_list("phone_number", flat=True)
    for num in users:
        print(num)
    