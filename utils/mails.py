from django.core.mail.message import EmailMultiAlternatives


class EmailMessage(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        """
        Takes three extra arguments
        - html_message: html version of message
        - file_paths: absolute paths of files which are to be attached with email
        """
        self.html_message = kwargs.pop("html_message", None)
        self.file_paths = kwargs.pop("file_paths", [])

        super(EmailMessage, self).__init__(*args, **kwargs)

        if self.html_message:
            self.attach_alternative(self.html_message, "text/html")

        for file_path in self.file_paths:
            self.attach_file(file_path)
