# Generated by Django 3.0.9 on 2022-02-07 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='place_number',
            field=models.IntegerField(default=0),
        ),
    ]
