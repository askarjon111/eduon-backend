# Generated by Django 3.0.9 on 2021-03-09 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='categoryImage/')),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('image', django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 346], upload_to='course/')),
                ('turi', models.CharField(choices=[('Bepul', 'Bepul'), ('Pullik', 'Pullik')], default='Pullik', max_length=8)),
                ('price', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('upload_or_youtube', models.CharField(choices=[('Youtube', 'Youtube'), ('Video', 'Video')], default='Youtube', max_length=15)),
                ('description', models.TextField(blank=True, max_length=350, null=True)),
                ('like', models.IntegerField(default=0)),
                ('dislike', models.IntegerField(default=0)),
                ('view', models.IntegerField(default=0)),
                ('is_top', models.IntegerField(default=0)),
                ('is_tavsiya', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('info', models.TextField(blank=True, max_length=500, null=True)),
                ('content1', models.TextField(blank=True, max_length=400, null=True)),
                ('content2', models.TextField(blank=True, max_length=400, null=True)),
                ('content3', models.TextField(blank=True, max_length=400, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='info/')),
            ],
        ),
        migrations.CreateModel(
            name='InfoWidget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('icon', models.CharField(blank=True, max_length=45, null=True)),
                ('content', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegBonus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summa', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('kasbi', models.CharField(max_length=250, null=True)),
                ('compony', models.CharField(max_length=250, null=True)),
                ('image', django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[128, 128], upload_to='imageSpeaker/')),
                ('image2', models.ImageField(null=True, upload_to='imagespeaker2/')),
                ('description', models.TextField(blank=True, max_length=650, null=True)),
                ('message', models.TextField(blank=True, max_length=650, null=True)),
                ('status', models.IntegerField(default=0)),
                ('is_top', models.IntegerField(default=0)),
                ('both_date', models.DateField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logo/')),
                ('speaker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=200)),
                ('first_name', models.CharField(blank=True, max_length=200, null=True)),
                ('last_name', models.CharField(blank=True, max_length=200, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='imageSpeaker/')),
                ('regdate', models.DateTimeField(auto_now_add=True)),
                ('last_sean', models.DateTimeField(blank=True, null=True)),
                ('cash', models.IntegerField(default=0)),
                ('age', models.DateField(blank=True, null=True)),
                ('job', models.CharField(blank=True, max_length=150, null=True)),
                ('bonus', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=0)),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.Country')),
                ('region', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.Region')),
            ],
        ),
        migrations.CreateModel(
            name='VideoCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField(default='', max_length=100)),
                ('video', models.FileField(default=None, upload_to='vidoeCourse/')),
                ('image', django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 346], upload_to='imageVideo/')),
                ('description', models.TextField(blank=True, max_length=650, null=True)),
                ('link', models.CharField(blank=True, max_length=255, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('views_count', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Speaker')),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.Course')),
            ],
        ),
        migrations.CreateModel(
            name='TopCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Course')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='service/')),
                ('content', models.ManyToManyField(to='home.ServiceContent')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summa', models.IntegerField(default=0)),
                ('invois', models.IntegerField(default=0)),
                ('payment_id', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
            ],
        ),
        migrations.CreateModel(
            name='EduonTafsiyasi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Course')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Speaker'),
        ),
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.CategoryVideo'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=500)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(default=0)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VideoViews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.VideoCourse')),
            ],
            options={
                'unique_together': {('user', 'video')},
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0)),
                ('ranked_date', models.DateTimeField(auto_now=True)),
                ('speaker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Speaker')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
            ],
            options={
                'unique_together': {('speaker', 'user')},
            },
        ),
        migrations.CreateModel(
            name='LikeOrDislike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], default=0)),
                ('voted_date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.VideoCourse')),
            ],
            options={
                'unique_together': {('user', 'video')},
            },
        ),
        migrations.CreateModel(
            name='FavoriteCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Users')),
            ],
            options={
                'unique_together': {('user', 'course')},
            },
        ),
    ]
