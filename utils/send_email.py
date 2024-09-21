from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
import os

email_backend = EmailBackend(
    host=os.getenv("EMAIL_HOST"),
    port=os.getenv("EMAIL_PORT"),
    username=os.getenv("EMAIL_HOST_USER"),
    password=os.getenv("EMAIL_HOST_PASSWORD"),
    # use_tls=os.getenv("EMAIL_USE_TLS", False),
    use_ssl=os.getenv("EMAIL_USE_SSL", True),
)


def send_email(subject, message, recipient_list, attachments=None, fail_silently=False):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=os.getenv("EMAIL_HOST_USER"),
        to=recipient_list,
        connection=email_backend,
    )

    if attachments:
        for attachment in attachments:
            email.attach(attachment['name'], attachment['content'], attachment['mime_type'])

    email.send(fail_silently=fail_silently)
