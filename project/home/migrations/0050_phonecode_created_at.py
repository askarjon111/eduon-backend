# Generated by Django 3.0.9 on 2022-01-24 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0049_auto_20220118_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonecode',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
