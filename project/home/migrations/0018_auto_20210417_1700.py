# Generated by Django 3.0.9 on 2021-04-17 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_auto_20210417_1654'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='video',
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(max_length=500),
        ),
    ]
