# Generated by Django 3.0.9 on 2021-04-15 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_course_discount'),
    ]

    operations = [
        migrations.CreateModel(
            name='RankCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('speaker_value', models.IntegerField(default=0)),
                ('course_value', models.IntegerField(default=0)),
                ('tashkil_value', models.IntegerField(default=0)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
            ],
            options={
                'unique_together': {('course', 'user')},
            },
        ),
    ]
