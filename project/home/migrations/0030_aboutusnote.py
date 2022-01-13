# Generated by Django 3.0.9 on 2021-08-10 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0029_auto_20210707_1743'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUsNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=15)),
                ('message', models.TextField()),
                ('is_seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
