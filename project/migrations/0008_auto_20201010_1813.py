# Generated by Django 3.0.3 on 2020-10-10 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20200914_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='refresh_token',
            field=models.CharField(default='', max_length=200, null=True),
        ),
    ]
