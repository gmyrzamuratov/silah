# Generated by Django 3.0.3 on 2020-10-29 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_calendar_currentproject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='frame',
            field=models.CharField(max_length=250),
        ),
    ]
