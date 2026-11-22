from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q


User = get_user_model()


class CustomBackend(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        identifier = (
            kwargs.get("identifier")
            or username
            or kwargs.get(User.USERNAME_FIELD)
        )

        if not identifier or not password:
            return None

        identifier = identifier.strip()

        user = User.objects.filter(
            Q(email__iexact=identifier)| Q(phone_number=identifier)
        )

        if user.count() != 1:
            # Perform a password hash to reduce timing differences
            # when an account does not exist or the identifier is ambiguous.
            make_password(password)
            return None

        user = user.first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def user_can_authenticate(self, user):

        # Delegate to Django's built-in check → is_active
        if not super().user_can_authenticate(user):
            return False

        # Patients can log in without email verification.
        if user.role == User.RoleChoices.PATIENT:
            return True

        # All other roles must verify their email.
        return user.is_verified