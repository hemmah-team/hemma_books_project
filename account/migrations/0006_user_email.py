# Generated by Django 5.2 on 2025-05-18 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_notification_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(default='ghelsdksd@fj.com', max_length=254, unique=True),
        ),
    ]
