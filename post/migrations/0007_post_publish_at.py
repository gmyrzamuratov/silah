# Generated by Django 3.0.3 on 2020-09-21 17:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0006_postvideos_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='publish_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]