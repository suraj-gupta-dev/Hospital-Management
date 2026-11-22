from django.contrib.auth import get_user_model
from django.utils import timezone


phone_numbers = [
    "+91-8976543210",
    "+91-8976543211",
    "+91-8976543212",
    "+91-8976543213",
    "+91-8976543214",
    "+91-8976543215",
    "+91-8976543216",
    "+91-8976543217",
    "+91-8976543218",
    "+91-8976543219",
    "+91-8975643210",
    "+91-8975643211",
    "+91-8975643212",
    "+91-8975643213",
    "+91-8975643214",
    "+91-8975643215",
    "+91-8975643216",
    "+91-8975643217",
    "+91-8975643218",
    "+91-8975643219",
    "+91-8974653210",
    "+91-8974653211",
    "+91-8974653212",
    "+91-8974653213",
    "+91-8974653214",
    "+91-8974653215",
    "+91-8974653216",
    "+91-8974653217",
    "+91-8974653218",
    "+91-8974653219",
    "+91-8974653220",
    "+91-8974653221",
    "+91-8974653222",
]

if len(phone_numbers) != len(set(phone_numbers)):
    raise ValueError("phone_numbers must contain only unique values")

def run():

# 1. updated_at Will Not Change Automatically

# Because bulk_update() bypasses Django’s model .save() method,
# any auto_now=True logic on updated_at will not run.
# Including "updated_at" in your list will just re-save
# its old timestamp unless you assign a new timestamp manually.

# 2. distinct("phone_number") Only Works on PostgreSQL

# Calling .distinct("phone_number") with a field name works on PostgreSQL,
# but will raise a NotSupportedError on MySQL, SQLite, or Oracle.
# Using .values("phone_number").distinct().count() works across all databases.

    User = get_user_model()

    users = User.objects.order_by("phone_number")
    print(len(users))

    for i, user in enumerate(users):
        user.phone_number = phone_numbers[i]
        user.update_at = timezone.now()

    User.objects.bulk_update(users, ["phone_number", "updated_at"])

    print(User.objects.distinct("phone_number").count())
