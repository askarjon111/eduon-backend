# Generated by Django 3.0.9 on 2021-04-17 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_rankcourse'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.VideoCourse'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(max_length=5000),
        ),
    ]
