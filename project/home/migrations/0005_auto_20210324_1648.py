# Generated by Django 3.0.9 on 2021-03-24 11:48

from django.db import migrations
import django_resized.forms
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20210322_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 346], upload_to=home.models.slugify_upload),
        ),
    ]
