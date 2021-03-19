from django.contrib import admin

from subjective_assignments.models import (SubjectiveAssignment, SubjectiveAssignmentHistory, SubjectiveAssignmentTeam)

class SubjectiveAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id','assignment_id', 'team_size')

class SubjectiveAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment_history', 'submitted_by', 'subjective_assignment_team')

class SubjectiveAssignmentTeamAdmin(admin.ModelAdmin):
    list_display = ('id'. 'user', 'subjective_assignment')

admin.site.register(SubjectiveAssignment, SubjectiveAssignmentAdmin)
admin.site.register(SubjectiveAssignmentHistory, SubjectiveAssignmentHistoryAdmin)
admin.site.register(SubjectiveAssignmentTeam, SubjectiveAssignmentTeamAdmin)