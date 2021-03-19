from django.contrib import admin

from leaderboard.models import (GradesHeader, GradesBody)

class GradesHeaderAdmin(admin.ModelAdmin):
    list_display = ('id','course', 'sheet_name')
    search_fields = ('course__title',)

class GradesBodyAdmin(admin.ModelAdmin):
    list_display = ('id','grades_header')

admin.site.register(GradesHeader, GradesHeaderAdmin)
admin.site.register(GradesBody, GradesBodyAdmin)
