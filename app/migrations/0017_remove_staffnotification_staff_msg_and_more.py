# Generated by Django 4.1.4 on 2022-12-26 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_remove_staffnotification_message_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffnotification',
            name='staff_msg',
        ),
        migrations.AddField(
            model_name='staffnotification',
            name='message',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
