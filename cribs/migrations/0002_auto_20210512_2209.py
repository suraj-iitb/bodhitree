# Generated by Django 3.2 on 2021-05-12 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cribs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='crib',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='cribreply',
            options={'ordering': ['-id']},
        ),
    ]