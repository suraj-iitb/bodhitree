from django.contrib import admin

from .models import (
    AdvancedProgrammingAssignment,
    AdvancedProgrammingAssignmentHistory,
    Assignment,
    AssignmentHistory,
    AssignmentSection,
    Exam,
    ExamHistory,
    SimpleProgrammingAssignment,
    SimpleProgrammingAssignmentHistory,
    TAAllocation,
    Testcase,
    TestcaseHistory,
)


class TAAllocationAdmin(admin.ModelAdmin):
    list_display = ("id", "mapping")


class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    search_fields = ("name", "description")


class AssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "user",
        "instructor_feedback",
        "created_on",
        "modified_on",
    )
    search_fields = ("user__email",)


class SimpleProgrammingAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "programming_language",
        "document",
    )
    search_fields = (
        "assignment__name",
        "assignment_description",
    )


class SimpleProgrammingAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment_history",
        "file_submitted",
    )
    search_fields = ("assignment_history__user__email",)


class AdvancedProgrammingAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "simple_programming_assignment",
        "helper_code",
        "instructor_solution_code",
        "files_to_be_submitted",
        "ta_allocation_file",
        "ta_allocation",
        "policy",
        "execution_time_calculate",
        "ignore_whitespaces_in_output",
        "indentation_percentage_calculate",
    )
    search_fields = (
        "simple_programming_assignment__assignment__name",
        "simple_programming_assignment__assignment__description",
    )


class AdvancedProgrammingAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "simple_programming_assignment_history",
        "execution_time",
        "indentation_percentage",
    )
    search_fields = (
        "simple_programming_assignment_history__assignment_history__user__email",
    )


class AssignmentSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "name",
        "description",
        "section_type",
        "compiler_command",
        "execution_command",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "name",
        "description",
    )


class TestcaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "assignment_section",
        "name",
        "cmd_line_args",
        "marks",
        "input_file",
        "output_file",
        "is_published",
        "created_on",
        "modified_on",
    )
    search_fields = ("name",)


class TestcaseHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "testcase",
        "marks_obtained",
    )
    search_fields = ("user__email",)


class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "duration",
        "late_duration",
        "allowed_ip_range",
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
admin.site.register(AdvancedProgrammingAssignment, AdvancedProgrammingAssignmentAdmin)
admin.site.register(
    AdvancedProgrammingAssignmentHistory, AdvancedProgrammingAssignmentHistoryAdmin
)
admin.site.register(AssignmentSection, AssignmentSectionAdmin)
admin.site.register(Testcase, TestcaseAdmin)
admin.site.register(TestcaseHistory, TestcaseHistoryAdmin)
