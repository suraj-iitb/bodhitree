from django.contrib import admin

from .models import Email


class EmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "sender",
        "from_email",
        "to",
        "reply_to",
        "cc",
        "bcc",
        "subject",
        "body",
        "sent_on",
    )
    search_fields = (
        "subject",
        "body",
    )


admin.site.register(Email, EmailAdmin)
