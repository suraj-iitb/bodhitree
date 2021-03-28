from django.contrib import admin

from .models import Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "body",
        "is_pinned",
        "created_on",
        "modified_on",
    )
    search_fields = ("body",)


admin.site.register(Announcement, AnnouncementAdmin)
