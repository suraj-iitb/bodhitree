# Generated by Django 3.1.6 on 2021-03-19 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cribs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crib',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
