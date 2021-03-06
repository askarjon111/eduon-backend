# Generated by Django 3.0.9 on 2021-03-22 17:58

from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20210319_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videocourse',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 346], upload_to='imageVideo/'),
        ),
        migrations.AlterField(
            model_name='videocourse',
            name='video',
            field=models.FileField(default=None, upload_to='vidoeCourse/'),
        ),
    ]
