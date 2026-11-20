from django.core.mail import send_mail


def run():
    send_mail(
        "Django Mailer",
        "Message from my hospital app",
        "agentgupta216@gmail.com",
        ["handsomearjun360@gmail.com"],
        using="default"
    )