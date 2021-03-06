# Generated by Django 3.0.9 on 2022-03-17 09:05

from django.db import migrations
import django_resized.forms
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0068_admin_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='image',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='JPEG', keep_meta=True, null=True, quality=75, size=[1920, 1080], upload_to=home.models.slugify_upload),
        ),
    ]
