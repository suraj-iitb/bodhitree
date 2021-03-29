from django.contrib import admin

from .models import (
    SubjectiveAssignment,
    SubjectiveAssignmentHistory,
    SubjectiveAssignmentTeam,
)


class SubjectiveAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "team_size",
        "question_file",
        "helper_file",
        "files_to_be_submitted",
    )
    search_fields = (
        "assignment__name",
        "assignment__description",
    )


class SubjectiveAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment_history",
        "submitted_file",
        "marks_obtained",
        "subjective_assignment_team",
    )
    search_fields = ("assignment_history__user__email",)


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
