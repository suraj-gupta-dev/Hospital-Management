from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db import transaction

from .models import FailedLoginAttempt, User


MAX_FAILED_ATTEMPTS = 2
LOCKOUT_DURATION = timedelta(minutes=15)


@transaction.atomic
def authenticate_with_lockout(email, password):
    """
    Authenticate a user and apply account lockout after
    MAX_FAILED_ATTEMPTS consecutive failed attempts.

    Returns: (user, is_locked)
    """
    email = User.objects.normalize_email(email.strip())

    # create or retrieve the tracking record
    attempt, create = FailedLoginAttempt.objects.get_or_create(email=email)

    # Lock this record while checking/updating its counter.
    attempt = FailedLoginAttempt.objects.select_for_update().get(
        pk=attempt.pk
    )


    # Reject login while the account is locked.
    if attempt.locked_until and attempt.locked_until >= timezone.now():
        return None, True

    # Reset an expired lockout.
    if attempt.locked_until and attempt.locked_until <= timezone.now():
        attempt.failed_attempts = 0
        attempt.locked_until = None
        attempt.save(update_fields=[
            "failed_attempts", "locked_until", "updated_at"
        ])

    # Try normal Django authentication.
    user = authenticate(email=email, password=password)

    if user is not None:
        # Successful login: clear the failure record.
        attempt.delete()
        return user, False

    # Failed login: increase the counter.
    attempt.failed_attempts += 1
    attempt.last_failed_at = timezone.now()

    # Lock the account after the fifth failure.
    if attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
        attempt.locked_until = timezone.now() + LOCKOUT_DURATION

    attempt.save(update_fields=[
        "failed_attempts",
        "last_failed_at",
        "locked_until",
        "updated_at",
    ])

    return None, False