from django.db import models
from django.contrib.postgres.fields import ArrayField
from course.models import (
    Chapter, Section
)
from django.conf import settings

class Quiz(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE,  null=True, blank=True)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    question_module_sequence = ArrayField(models.IntegerField(), null=True, blank=True)    
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class QuestionModule(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    questions_sequence = ArrayField(models.IntegerField(), null=True, blank=True)    
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz_module = models.ForeignKey(QuestionModule, on_delete=models.CASCADE)
    question_description = models.TextField()                             
    answer_description = models.TextField()                               
    hint = models.TextField(blank=True)
    max_no_of_attempts = models.IntegerField(blank=True, null=True)
    marks = models.IntegerField(default=0)
    gradable = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_description

class QuestionHistory(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    no_of_times_attempted = models.IntegerField()
    marks_obtained = models.IntegerField(null=True, blank=True)
    hint_taken = models.BooleanField(default=False)

    def __str__(self):
        return self.question.question_description

class SingleCorrectQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    options = ArrayField(models.TextField())    
    correct_option = models.IntegerField()

class SingleCorrectQuestionHistory(models.Model):
    question_history = models.ForeignKey(QuestionHistory, on_delete=models.CASCADE)
    option_selected = models.IntegerField()

class MultipleCorrectQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    options = ArrayField(models.TextField())    
    correct_option = ArrayField(models.IntegerField())

class MulitpleCorrectQuestionHistory(models.Model):
    question_history = models.ForeignKey(QuestionHistory, on_delete=models.CASCADE)
    option_selected = ArrayField(models.IntegerField())

class FixedAnswerQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()

class FixedCorrectQuestionHistory(models.Model):
    question_history = models.ForeignKey(QuestionHistory, on_delete=models.CASCADE)
    answer_submitted = models.TextField()

class DescriptiveQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()

class DescriptiveQuestionHistory(models.Model):
    question_history = models.ForeignKey(QuestionHistory, on_delete=models.CASCADE)
    answer_submitted = models.TextField()

