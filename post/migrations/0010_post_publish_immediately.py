# Generated by Django 3.0.3 on 2020-10-27 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0009_auto_20201026_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='publish_immediately',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
