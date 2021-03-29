from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from course.models import Chapter, Section


class Quiz(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, null=True, blank=True
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    question_module_sequence = ArrayField(models.IntegerField(), null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class QuestionModule(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    questions_sequence = ArrayField(models.IntegerField(), null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    question_module = models.ForeignKey(QuestionModule, on_delete=models.CASCADE)
    question_description = models.TextField()
    answer_description = models.TextField()
    hint = models.TextField(blank=True)
    max_no_of_attempts = models.IntegerField(blank=True, null=True)
    marks = models.IntegerField(default=0)
    gradable = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}...".format(self.question_description[0:20])


class QuestionHistory(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    no_of_times_attempted = models.IntegerField(default=0)
    marks_obtained = models.IntegerField(null=True, blank=True)
    hint_taken = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}...".format(self.user.email, self.question_description[0:20])


class SingleCorrectQuestion(Question):
    options = ArrayField(models.TextField())
    correct_option = models.IntegerField()


class SingleCorrectQuestionHistory(QuestionHistory):
    option_selected = models.IntegerField()


class MultipleCorrectQuestion(Question):
    options = ArrayField(models.TextField())
    correct_options = ArrayField(models.IntegerField())


class MulitpleCorrectQuestionHistory(QuestionHistory):
    options_selected = ArrayField(models.IntegerField())


class FixedAnswerQuestion(Question):
    answer = models.TextField()


class FixedCorrectQuestionHistory(QuestionHistory):
    answer_submitted = models.TextField()


class DescriptiveQuestion(Question):
    answer = models.TextField()


class DescriptiveQuestionHistory(QuestionHistory):
    answer_submitted = models.TextField()
