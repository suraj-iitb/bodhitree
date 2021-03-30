# Generated by Django 3.1.6 on 2021-03-30 04:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programming_assignments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcase',
            name='assignment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='programming_assignments.assignment'),
        ),
        migrations.AlterField(
            model_name='testcase',
            name='assignment_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='programming_assignments.assignmentsection'),
        ),
        migrations.AddConstraint(
            model_name='testcase',
            constraint=models.CheckConstraint(check=models.Q(('assignment__isnull', False), ('assignment_section__isnull', False), _connector='OR'), name='both_not_null_in_testcase'),
        ),
    ]
