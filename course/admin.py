from django.contrib import admin
from course.models import (Course, CourseHistory, Chapter, Section, Notification, Schedule, Page)
from course.models import Course

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'title', 'course_type')
    search_fields = ('title',)

class CourseHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'role')
    search_fields = ('course__title','user__email')

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'name')
    search_fields = ('course__title',)

class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter', 'name')
    search_fields = ('chapter__name',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title')
    search_fields = ('course__title', 'title')

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'start_date', 'end_date')
    search_fields = ('course__title',)

class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title')
    search_fields = ('course__title', 'title')


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseHistory, CourseHistoryAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Page, PageAdmin)