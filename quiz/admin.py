from django.contrib import admin

from quiz.models import (
    DescriptiveQuestion,
    DescriptiveQuestionHistory,
    FixedAnswerQuestion,
    FixedCorrectQuestionHistory,
    MulitpleCorrectQuestionHistory,
    MultipleCorrectQuestion,
    QuestionModule,
    Quiz,
    SingleCorrectQuestion,
    SingleCorrectQuestionHistory,
)


class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "chapter",
        "section",
        "description",
        "question_module_sequence",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "title",
        "description",
    )


class QuestionModuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quiz",
        "title",
        "description",
        "questions_sequence",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "title",
        "description",
    )


class SingleCorrectQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question_module",
        "question_description",
        "answer_description",
        "hint",
        "max_no_of_attempts",
        "marks",
        "gradable",
        "is_published",
        "options",
        "correct_option",
        "created_on",
        "modified_on",
    )
    search_fields = ("question_description",)


class SingleCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "user",
        "no_of_times_attempted",
        "marks_obtained",
        "hint_taken",
        "option_selected",
        "created_on",
        "modified_on",
    )
    search_fields = ("user__email",)


class MultipleCorrectQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question_module",
        "question_description",
        "answer_description",
        "hint",
        "max_no_of_attempts",
        "marks",
        "gradable",
        "is_published",
        "options",
        "correct_options",
        "created_on",
        "modified_on",
    )
    search_fields = ("question_description",)


class MulitpleCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "user",
        "no_of_times_attempted",
        "marks_obtained",
        "hint_taken",
        "options_selected",
        "created_on",
        "modified_on",
    )
    search_fields = ("user__email",)


class FixedAnswerQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question_module",
        "question_description",
        "answer_description",
        "hint",
        "max_no_of_attempts",
        "marks",
        "gradable",
        "is_published",
        "answer",
        "created_on",
        "modified_on",
    )
    search_fields = ("question_description",)


class FixedCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "user",
        "no_of_times_attempted",
        "marks_obtained",
        "hint_taken",
        "answer_submitted",
        "created_on",
        "modified_on",
    )
    search_fields = ("user__email",)


class DescriptiveQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question_module",
        "question_description",
        "answer_description",
        "hint",
        "max_no_of_attempts",
        "marks",
        "gradable",
        "is_published",
        "answer",
        "created_on",
        "modified_on",
    )
    search_fields = ("question_description",)


class DescriptiveQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "user",
        "no_of_times_attempted",
        "marks_obtained",
        "hint_taken",
        "answer_submitted",
        "created_on",
        "modified_on",
    )
    search_fields = ("user__email",)


admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuestionModule, QuestionModuleAdmin)
admin.site.register(SingleCorrectQuestion, SingleCorrectQuestionAdmin)
admin.site.register(SingleCorrectQuestionHistory, SingleCorrectQuestionHistoryAdmin)
admin.site.register(MultipleCorrectQuestion, MultipleCorrectQuestionAdmin)
admin.site.register(MulitpleCorrectQuestionHistory, MulitpleCorrectQuestionHistoryAdmin)
admin.site.register(FixedAnswerQuestion, FixedAnswerQuestionAdmin)
admin.site.register(FixedCorrectQuestionHistory, FixedCorrectQuestionHistoryAdmin)
admin.site.register(DescriptiveQuestion, DescriptiveQuestionAdmin)
admin.site.register(DescriptiveQuestionHistory, DescriptiveQuestionHistoryAdmin)
