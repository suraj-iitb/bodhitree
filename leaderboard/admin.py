from django.contrib import admin

from leaderboard.models import MarksBody, MarksHeader


class MarksHeaderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "sheet_name",
        "header_list",
        "created_on",
        "modified_on",
    )
    search_fields = ("sheet_name",)


class MarksBodyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "marks_header",
        "student_marks",
        "created_on",
        "modified_on",
    )
    search_fields = ("student_marks",)


admin.site.register(MarksHeader, MarksHeaderAdmin)
admin.site.register(MarksBody, MarksBodyAdmin)
