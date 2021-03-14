from django.contrib import admin

from programming_assignments.models import (TAAllocation, Assignment, AssignmentHistory, SimpleProgrammingAssignment, SimpleProgrammingAssignmentHistory,
SimpleProgrammingAssignmentHistoryVersion, AdvancedProgrammingAssignment, AdvancedProgrammingAssignmentHistory,  AdvancedProgrammingAssignmentHistoryVersion, AssignmentSection, Testcase, TestcaseHistory)

class TAAllocationAdmin(admin.ModelAdmin):
    list_display = ('id','mapping')

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id','course', 'name')

class AssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','assignment' , 'user')

class SimpleProgrammingAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id','assignment')

class SimpleProgrammingAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment_history')

class SimpleProgrammingAssignmentHistoryVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'simple_programming_assignment_history')

class AdvancedProgrammingAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'simple_programming_assignment' , 'ta_allocation')

class AdvancedProgrammingAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'simple_programming_assignment')

class AdvancedProgrammingAssignmentHistoryVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'advanced_programming_assignment_history')

class AssignmentSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'name', 'section_type')

class TestcaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'assignment_section', 'name', 'marks')

class TestcaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

admin.site.register(TAAllocation, TAAllocationAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentHistory, AssignmentHistoryAdmin)
admin.site.register(SimpleProgrammingAssignment, SimpleProgrammingAssignmentAdmin)
admin.site.register(SimpleProgrammingAssignmentHistory, SimpleProgrammingAssignmentHistoryAdmin)
admin.site.register(SimpleProgrammingAssignmentHistoryVersion, SimpleProgrammingAssignmentHistoryVersionAdmin)
admin.site.register(AdvancedProgrammingAssignment, AdvancedProgrammingAssignmentAdmin)
admin.site.register(AdvancedProgrammingAssignmentHistory, AdvancedProgrammingAssignmentHistoryAdmin)
admin.site.register(AdvancedProgrammingAssignmentHistoryVersion, AdvancedProgrammingAssignmentHistoryVersionAdmin)
admin.site.register(AssignmentSection, AssignmentSectionAdmin)
admin.site.register(Testcase, TestcaseAdmin)
admin.site.register(TestcaseHistory, TestcaseHistoryAdmin)

#instead of foreign key object, display proper name of foreign key attribute. Change in all tables