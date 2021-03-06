# Generated by Django 3.2 on 2021-05-03 13:08

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import subjective_assignments.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programming_assignments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectiveAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_size', models.IntegerField(default=1)),
                ('question_file', models.FileField(upload_to=subjective_assignments.models.subjective_assignment_file_upload_path)),
                ('helper_file', models.FileField(blank=True, null=True, upload_to=subjective_assignments.models.subjective_assignment_file_upload_path)),
                ('files_to_be_submitted', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None)),
                ('assignment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='programming_assignments.assignment')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectiveAssignmentTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_ids', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('subjective_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjective_assignments.subjectiveassignment')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectiveAssignmentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_file', django.contrib.postgres.fields.ArrayField(base_field=models.FileField(upload_to=subjective_assignments.models.subjective_assignment_file_upload_path), blank=True, null=True, size=None)),
                ('marks_obtained', models.FloatField(default=0)),
                ('assignment_history', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='programming_assignments.assignmenthistory')),
                ('subjective_assignment_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjective_assignments.subjectiveassignmentteam')),
            ],
        ),
    ]
