# Generated by Django 3.0.3 on 2020-11-02 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0012_remove_post_publish_immediately'),
    ]

    operations = [
        migrations.AddField(
            model_name='postphotos',
            name='order',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
