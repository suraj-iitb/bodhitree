# Generated by Django 3.1.6 on 2021-03-20 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_auto_20210319_2116'),
        ('course', '0003_auto_20210319_1945'),
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marker',
            name='marker_type',
            field=models.CharField(choices=[('S', 'Section marker'), ('Q', 'Quiz marker')], max_length=1),
        ),
        migrations.AlterField(
            model_name='quizmarker',
            name='marker',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='video.marker'),
        ),
        migrations.AlterField(
            model_name='quizmarker',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz'),
        ),
        migrations.AlterField(
            model_name='quizmarker',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='sectionmarker',
            name='marker',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='video.marker'),
        ),
        migrations.AlterField(
            model_name='sectionmarker',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='video',
            name='chapter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.chapter'),
        ),
        migrations.AlterField(
            model_name='video',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.section'),
        ),
        migrations.AlterField(
            model_name='video',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]