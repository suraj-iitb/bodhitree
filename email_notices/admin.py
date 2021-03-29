from django.contrib import admin

from email_notices.models import Email


class EmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "sender",
        "from_email",
        "to_email_list",
        "reply_to",
        "cc_list",
        "subject",
        "body",
        "sent_on",
    )
    search_fields = (
        "subject",
        "body",
    )


admin.site.register(Email, EmailAdmin)
