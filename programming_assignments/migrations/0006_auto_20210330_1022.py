# Generated by Django 3.1.6 on 2021-03-30 04:52

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('programming_assignments', '0005_auto_20210330_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 3, 30, 4, 52, 35, 906759, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exam',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='examhistory',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 3, 30, 4, 52, 47, 380424, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='examhistory',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='testcasehistory',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 3, 30, 4, 52, 55, 570179, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testcasehistory',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
