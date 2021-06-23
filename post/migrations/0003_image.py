# Generated by Django 3.0.3 on 2020-08-22 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_postimages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255)),
                ('file', models.FileField(upload_to='images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]