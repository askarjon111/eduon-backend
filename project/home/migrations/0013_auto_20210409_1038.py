# Generated by Django 3.0.9 on 2021-04-09 05:38

from django.db import migrations
import django_resized.forms
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_videocourse_place_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 400], upload_to=home.models.slugify_upload),
        ),
        migrations.AlterField(
            model_name='videocourse',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 400], upload_to=home.models.slugify_upload),
        ),
    ]
