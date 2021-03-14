from django.contrib import admin

from course.models import Course, CourseHistory, Chapter, Section, Notification, Schedule

admin.site.register(CourseHistory)
admin.site.register(Chapter)
admin.site.register(Section)
admin.site.register(Notification)
admin.site.register(Schedule)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'title')

admin.site.register(Course, CourseAdmin)