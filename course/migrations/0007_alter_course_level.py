# Generated by Django 4.0.8 on 2023-06-19 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_courseoffer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='level',
            field=models.CharField(choices=[('Intro', 'Intro Degree'), ('Middle', 'Middle Degree')], max_length=25, null=True),
        ),
    ]
