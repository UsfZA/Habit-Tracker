# Generated by Django 4.1 on 2024-04-16 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('habit', '0027_alter_habit_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='habit',
            name='status',
        ),
    ]
