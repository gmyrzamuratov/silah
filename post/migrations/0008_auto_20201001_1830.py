# Generated by Django 3.0.3 on 2020-10-01 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0007_post_publish_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='publish_at',
            field=models.DateTimeField(),
        ),
    ]
