from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
import os

email_backend = EmailBackend(
    host=os.getenv["EMAIL_HOST"],
    port=os.getenv["EMAIL_PORT"],
    username=os.getenv["EMAIL_HOST_USER"],
    password=os.getenv["EMAIL_HOST_PASSWORD"],
    use_tls=os.getenv("EMAIL_USE_TLS", False),
    use_ssl=os.getenv("EMAIL_USE_SSL", False),
)


def send_email(subject, message, recipient_list, fail_silently=False):
    send_mail(
        subject=subject,
        message=message,
        from_email=os.getenv["EMAIL_HOST_USER"],
        recipient_list=recipient_list,
        fail_silently=fail_silently,
        connection=email_backend,
    )
