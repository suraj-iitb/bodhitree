# Generated by Django 3.1.6 on 2021-03-28 16:28

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_description', models.TextField()),
                ('answer_description', models.TextField()),
                ('hint', models.TextField(blank=True)),
                ('max_no_of_attempts', models.IntegerField(blank=True, null=True)),
                ('marks', models.IntegerField(default=0)),
                ('gradable', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_times_attempted', models.IntegerField()),
                ('marks_obtained', models.IntegerField(blank=True, null=True)),
                ('hint_taken', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SingleCorrectQuestionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_selected', models.IntegerField()),
                ('question_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.questionhistory')),
            ],
        ),
        migrations.CreateModel(
            name='SingleCorrectQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('options', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('correct_option', models.IntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('question_module_sequence', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.chapter')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.section')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('questions_sequence', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='quiz_module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.questionmodule'),
        ),
        migrations.CreateModel(
            name='MultipleCorrectQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('options', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('correct_option', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
            ],
        ),
        migrations.CreateModel(
            name='MulitpleCorrectQuestionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_selected', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('question_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.questionhistory')),
            ],
        ),
        migrations.CreateModel(
            name='FixedCorrectQuestionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_submitted', models.TextField()),
                ('question_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.questionhistory')),
            ],
        ),
        migrations.CreateModel(
            name='FixedAnswerQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
            ],
        ),
        migrations.CreateModel(
            name='DescriptiveQuestionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_submitted', models.TextField()),
                ('question_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.questionhistory')),
            ],
        ),
        migrations.CreateModel(
            name='DescriptiveQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
            ],
        ),
    ]
