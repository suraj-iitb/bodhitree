# Generated by Django 3.2 on 2021-05-15 04:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import video.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('video_file', models.FileField(upload_to=video.models.video_upload_path)),
                ('doc_file', models.FileField(blank=True, null=True, upload_to=video.models.video_doc_upload_path)),
                ('in_video_quiz_file', models.FileField(blank=True, null=True, upload_to=video.models.in_video_quiz_upload_path)),
                ('video_duration', models.DurationField()),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.chapter')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.section')),
            ],
        ),
        migrations.CreateModel(
            name='VideoHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_watched_duration', models.DurationField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='video.video')),
            ],
        ),
        migrations.CreateModel(
            name='SectionMarker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DurationField()),
                ('title', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='video.video')),
            ],
        ),
        migrations.CreateModel(
            name='QuizMarker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DurationField()),
                ('title', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('quiz', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='video.video')),
            ],
        ),
        migrations.AddConstraint(
            model_name='video',
            constraint=models.CheckConstraint(check=models.Q(('chapter__isnull', False), ('section__isnull', False), _connector='OR'), name='both_not_null_in_video'),
        ),
        migrations.AddConstraint(
            model_name='sectionmarker',
            constraint=models.UniqueConstraint(fields=('video', 'time'), name='unique_section_marker'),
        ),
        migrations.AddConstraint(
            model_name='quizmarker',
            constraint=models.UniqueConstraint(fields=('video', 'time'), name='unique_quiz_marker'),
        ),
    ]
