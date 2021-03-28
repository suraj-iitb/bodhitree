from django.contrib import admin

from programming_assignments.models import (
    AdvancedProgrammingAssignment,
    AdvancedProgrammingAssignmentHistory,
    AdvancedProgrammingAssignmentHistoryVersion,
    Assignment,
    AssignmentHistory,
    AssignmentSection,
    Exam,
    ExamHistory,
    SimpleProgrammingAssignment,
    SimpleProgrammingAssignmentHistory,
    SimpleProgrammingAssignmentHistoryVersion,
    TAAllocation,
    Testcase,
    TestcaseHistory,
)


class TAAllocationAdmin(admin.ModelAdmin):
    list_display = ("id", "mapping")


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "name")
    search_fields = ("course__title", "name")


class AssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment", "user")
    search_fields = ("assignment__name", "user__email")


class SimpleProgrammingAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment")
    search_fields = ("assignment__name",)


class SimpleProgrammingAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment_history")
    search_fields = ("assignment_history__user__email",)


class SimpleProgrammingAssignmentHistoryVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "simple_programming_assignment_history")


class AdvancedProgrammingAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "simple_programming_assignment", "ta_allocation")
    search_fields = ("simple_programming_assignment__assignment__name",)


class AdvancedProgrammingAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "simple_programming_assignment")
    search_fields = (
        "simple_programming_assignment_history__assignment_history__user__email",
    )


class AdvancedProgrammingAssignmentHistoryVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "advanced_programming_assignment_history")


class AssignmentSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment", "name", "section_type")
    search_fields = ("assignment__name", "name", "section_type")


class TestcaseAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment", "assignment_section", "name", "marks")
    search_fields = ("assignment__name", "name", "assignment_section__name")


class TestcaseHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__email",)


class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "duration",
        "late_duration",
        "allowed_ip_range",
        "assignment",
    )
    search_fields = ("assignment__name",)


class ExamHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exam",
        "user",
        "ip_address",
        "is_paused",
        "is_approved",
        "start_time",
        "remaining_time",
        "additional_time",
    )
    search_fields = ("user__email",)


admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamHistory, ExamHistoryAdmin)
admin.site.register(TAAllocation, TAAllocationAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentHistory, AssignmentHistoryAdmin)
admin.site.register(SimpleProgrammingAssignment, SimpleProgrammingAssignmentAdmin)
admin.site.register(
    SimpleProgrammingAssignmentHistory, SimpleProgrammingAssignmentHistoryAdmin
)
admin.site.register(
    SimpleProgrammingAssignmentHistoryVersion,
    SimpleProgrammingAssignmentHistoryVersionAdmin,
)
admin.site.register(AdvancedProgrammingAssignment, AdvancedProgrammingAssignmentAdmin)
admin.site.register(
    AdvancedProgrammingAssignmentHistory, AdvancedProgrammingAssignmentHistoryAdmin
)
admin.site.register(
    AdvancedProgrammingAssignmentHistoryVersion,
    AdvancedProgrammingAssignmentHistoryVersionAdmin,
)
admin.site.register(AssignmentSection, AssignmentSectionAdmin)
admin.site.register(Testcase, TestcaseAdmin)
admin.site.register(TestcaseHistory, TestcaseHistoryAdmin)
