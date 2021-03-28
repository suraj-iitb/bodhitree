from django.contrib import admin

from .models import (
    Announcement,
    Chapter,
    Course,
    CourseHistory,
    Notification,
    Page,
    Schedule,
    Section,
)


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "code",
        "title",
        "description",
        "image",
        "is_published",
        "course_type",
        "created_on",
        "modified_on",
        "chapters_sequence",
    )
    search_fields = (
        "code",
        "title",
        "description",
    )


class CourseHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "course",
        "role",
        "status",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "user__email",
        "user__full_name",
    )


class ChapterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "title",
        "description",
        "content_sequence",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "title",
        "description",
    )


class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chapter",
        "title",
        "description",
        "content_sequence",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "title",
        "description",
    )


class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "title",
        "url",
        "created_on",
    )
    search_fields = (
        "title",
        "url",
    )


class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "start_date",
        "end_date",
        "description",
        "content_list",
        "created_on",
        "modified_on",
    )
    search_fields = ("description",)


class PageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "title",
        "description",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "title",
        "description",
    )


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


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseHistory, CourseHistoryAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
