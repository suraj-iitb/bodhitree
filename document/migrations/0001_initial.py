# Generated by Django 3.1.6 on 2021-03-28 16:28

from django.db import migrations, models
import django.db.models.deletion
import document.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=75)),
                ('description', models.TextField(blank=True)),
                ('doc_file', models.FileField(upload_to=document.models.document_upload_path)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.chapter')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.section')),
            ],
        ),
    ]
