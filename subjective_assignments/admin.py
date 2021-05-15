from django.contrib import admin

from .models import (
    SubjectiveAssignment,
    SubjectiveAssignmentHistory,
    SubjectiveAssignmentTeam,
)


class SubjectiveAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "team_size",
        "question_file",
        "helper_file",
        "files_to_be_submitted",
        "course",
        "name",
        "description",
        "is_published",
        "start_date",
        "end_date",
        "extended_date",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "name",
        "description",
    )


class SubjectiveAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "instructor_feedback",
        "created_on",
        "modified_on",
        "submitted_file",
        "marks_obtained",
        "subjective_assignment_team",
    )
    search_fields = ("user__email",)


class SubjectiveAssignmentTeamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_ids",
        "subjective_assignment",
    )
    search_fields = ("user_ids",)


admin.site.register(SubjectiveAssignment, SubjectiveAssignmentAdmin)
admin.site.register(SubjectiveAssignmentHistory, SubjectiveAssignmentHistoryAdmin)
admin.site.register(SubjectiveAssignmentTeam, SubjectiveAssignmentTeamAdmin)
