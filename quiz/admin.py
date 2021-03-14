from django.contrib import admin

from quiz.models import (Quiz, QuestionModule, Question, QuestionHistory, SingleCorrectQuestion, SingleCorrectQuestionHistory, MultipleCorrectQuestion,
MulitpleCorrectQuestionHistory, FixedAnswerQuestion, FixedCorrectQuestionHistory, DescriptiveQuestion, DescriptiveQuestionHistory)

class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter', 'section')

class QuestionModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'quiz')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_module' ,'question_description', 'answer_description')

class QuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'no_of_times_attempted')

class SingleCorrectQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'options', 'correct_option')

class SingleCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'option_selected')

class MultipleCorrectQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'options', 'correct_option')

class MulitpleCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'option_selected')

class FixedAnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer')

class FixedCorrectQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'answer_submitted')

class DescriptiveQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer')

class DescriptiveQuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_history', 'answer_submitted')

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
