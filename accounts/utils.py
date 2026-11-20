from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings




class StaffEmailVerificationService:
    VERIFICATION_SALT = "staff-email-verification"
    VERIFICATION_MAX_AGE = 60 * 60  # 1 hours

    @classmethod
    def generate_staff_verification_token(cls, user):
        return signing.dumps(
            {"user_id": str(user.pk)},
            salt=cls.VERIFICATION_SALT
        )

    @classmethod
    def send_verification_email(cls, request, user):
        token = cls.generate_staff_verification_token(user)
        path = reverse("verify-staff-email")
        verification_url = f"{request.build_absolute_uri(path)}?token={token}"
        print(verification_url)

        subject = "Verify your hospital staff account"
        message = f"""
                    Hello {user.first_name},

                    Your staff account has been created successfully.

                    Please verify your email address using the link below:

                    {verification_url}

                    This link will expire in 24 hours.

                    If you did not expect this email, please contact your hospital administrator.
                """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )