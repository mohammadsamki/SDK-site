# Generated by Django 4.0.8 on 2023-06-19 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_alter_choice_id_alter_progress_id_alter_question_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='figure',
            field=models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d', verbose_name='Figure'),
        ),
    ]
