# Generated by Django 3.1.6 on 2021-03-19 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionmodule',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
