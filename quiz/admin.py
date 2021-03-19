from django.contrib import admin

from quiz.models import (Quiz, QuestionModule, Question, QuestionHistory, SingleCorrectQuestion, SingleCorrectQuestionHistory, MultipleCorrectQuestion,
MulitpleCorrectQuestionHistory, FixedAnswerQuestion, FixedCorrectQuestionHistory, DescriptiveQuestion, DescriptiveQuestionHistory)

class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter', 'section')
    search_fields = ('title', 'chapter__name', 'section__name')

class QuestionModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'quiz')
    search_fields = ('title', 'quiz__title')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_module' ,'question_description', 'answer_description')
    search_fields = ('question_description', 'quiz_module__title')

class QuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'no_of_times_attempted')
    search_fields = ('question__question_description', 'user__email')

class SingleCorrectQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'options', 'correct_option')
    search_fields = ('question__question_description',)

class SingleCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'option_selected')
    search_fields = ('question_history__question__question_description', 'question_history__user__email')

class MultipleCorrectQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'options', 'correct_option')
    search_fields = ('question__question_description',)

class MulitpleCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'option_selected')
    search_fields = ('question_history__question__question_description', 'question_history__user__email')

class FixedAnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer')
    search_fields = ('question__question_description',)

class FixedCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'answer_submitted')
    search_fields = ('question_history__question__question_description', 'question_history__user__email')

class DescriptiveQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer')
    search_fields = ('question__question_description',)

class DescriptiveQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'answer_submitted')
    search_fields = ('question_history__question__question_description', 'question_history__user__email')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuestionModule, QuestionModuleAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionHistory, QuestionHistoryAdmin)
admin.site.register(SingleCorrectQuestion, SingleCorrectQuestionAdmin)
admin.site.register(SingleCorrectQuestionHistory, SingleCorrectQuestionHistoryAdmin)
admin.site.register(MultipleCorrectQuestion, MultipleCorrectQuestionAdmin)
admin.site.register(MulitpleCorrectQuestionHistory, MulitpleCorrectQuestionHistoryAdmin)
admin.site.register(FixedAnswerQuestion, FixedAnswerQuestionAdmin)
admin.site.register(FixedCorrectQuestionHistory, FixedCorrectQuestionHistoryAdmin)
admin.site.register(DescriptiveQuestion, DescriptiveQuestionAdmin)
admin.site.register(DescriptiveQuestionHistory, DescriptiveQuestionHistoryAdmin)
