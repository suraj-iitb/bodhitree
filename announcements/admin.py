from django.contrib import admin

from announcements.models import Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "is_pinned")
    search_fields = ("course__title",)


admin.site.register(Announcement, AnnouncementAdmin)
