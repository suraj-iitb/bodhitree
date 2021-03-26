from django.contrib import admin

from subjective_assignments.models import (SubjectiveAssignment,
                                           SubjectiveAssignmentHistory,
                                           SubjectiveAssignmentTeam)


class SubjectiveAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment_id', 'team_size')
    search_fields = ('assignment__name',)


class SubjectiveAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment_history', 'submitted_by',
                    'subjective_assignment_team')
    search_fields = ('submitted_by__email',)


class SubjectiveAssignmentTeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subjective_assignment')
    search_fields = ('user__email',)


admin.site.register(SubjectiveAssignment, SubjectiveAssignmentAdmin)
admin.site.register(SubjectiveAssignmentHistory,
                    SubjectiveAssignmentHistoryAdmin)
admin.site.register(SubjectiveAssignmentTeam, SubjectiveAssignmentTeamAdmin)
