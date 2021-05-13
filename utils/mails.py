from django.core import mail
from django.core.mail.message import EmailMultiAlternatives


class EmailMessage(EmailMultiAlternatives):
    """Email Message"""

    def __init__(self, *args, **kwargs):
        self.html_message = kwargs.pop("html_message", None)
        self.file_paths = kwargs.pop("file_paths", [])

        super(EmailMessage, self).__init__(*args, **kwargs)

        if self.html_message:
            self.attach_alternative(self.html_message, "text/html")

        for file_path in self.file_paths:
            self.attach_file(file_path)


def send_mail(
    subject,
    body,
    from_email,
    to,
    cc=[],
    bcc=[],
    reply_to=None,
    html_message=None,
    file_paths=[],
):
    """Sends an email

    Args:
        subject (str): Email subject
        body (str): Email body
        from_email (str): Email id of sender
        to (list): List of email id of receiver
        cc (list, optional): List of email id to cc. Defaults to [].
        bcc (list, optional): List of email id for bcc. Defaults to [].
        reply_to (str, optional): Email id to reply to. Defaults to None.
        html_message (str, optional): HTML message. Defaults to None.
        file_paths (list, optional): List of file attachments. Defaults to [].
    """
    with mail.get_connection() as connection:

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to,
            cc=cc,
            bcc=bcc,
            connection=connection,
            reply_to=reply_to,
            html_message=html_message,
            file_paths=file_paths,
        )
        email.send()
