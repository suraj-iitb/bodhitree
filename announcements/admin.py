from django.contrib import admin

from announcements.models import Announcement

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'is_pinned')

admin.site.register(Announcement, AnnouncementAdmin)
