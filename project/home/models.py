import secrets
import string
from os.path import splitext

from django.contrib.auth.hashers import make_password
from django_resized import ResizedImageField
from django.contrib.auth.models import User
from django.db import models, migrations

from transliterate.utils import _, slugify


from uniredpay.uniredpay_conf import wallet_api


def make_many_categories(apps, schema_editor):
    """
        Adds the Author object in Book.author to the
        many-to-many relationship in Book.authors
    """
    Course = apps.get_model('home', 'Course')

    for course in Course.objects.all():
        course.categories.add(course.category)
        course.save()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0046_auto_20220115_1155'),
    ]

    operations = [
        migrations.RunPython(make_many_categories),
    ]


def generate_ref():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return password


class PhoneCode(models.Model):
    phone = models.CharField(max_length=25)
    code = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.phone


class PhoneCodeSpeaker(models.Model):
    phone = models.CharField(max_length=25)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.phone


def slugify_upload(instance, filename):
    folder = instance._meta.model.__name__
    name, ext = splitext(filename)
    try:

        name_t = slugify(name)
        if name_t is None:
            name_t = name
        path = folder + "/" + name_t + ext
    except:
        path = folder + "/default" + ext

    return path


class Permissions(models.Model):
    name = models.CharField(max_length=255)
    status = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Admin(models.Model):
    permessions = (
        (1, "Super admin"),
        (2, "Speakerlar bo'limi"),
        (3, "Foydalanuvchilar bo'limi"),
        (4, "Kurslar bo'limi"),
        (5, "Moliya bo'limi"),
        (6, "Tasdiq bo'limi"),
        (7, "To'lov bo'limi"),
        (8, "Sozlamalar bo'limi"),
        (9, "Dashboard bo'limi"),
    )
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ManyToManyField(Permissions)

    def __str__(self):
        return self.admin.username


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Davlat"
        verbose_name_plural = "Davlatlar"


class InfoWidget(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    icon = models.CharField(max_length=45, null=True, blank=True)
    content = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title or "-"


class ServiceContent(models.Model):
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class ServiceInfo(models.Model):
    title = models.CharField(max_length=255)
    content = models.ManyToManyField(ServiceContent)
    image = models.ImageField(upload_to=slugify_upload)

    def __str__(self):
        return self.title


class Info(models.Model):
    title = models.CharField(max_length=255)
    info = models.TextField(max_length=500, null=True, blank=True)
    content1 = models.TextField(max_length=400, null=True, blank=True)
    content2 = models.TextField(max_length=400, null=True, blank=True)
    content3 = models.TextField(max_length=400, null=True, blank=True)
    image = models.ImageField(upload_to=slugify_upload, null=True, blank=True)

    def __str__(self):
        return self.title


class Region(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"


class RegBonus(models.Model):
    summa = models.IntegerField(default=0)
    summa_full = models.IntegerField(default=0)


class ReferalValue(models.Model):
    user_value = models.IntegerField(default=0)
    speaker_value = models.IntegerField(default=0)


class Speaker(models.Model):
    speaker = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True)
    kasbi = models.CharField(max_length=250, null=True)
    compony = models.CharField(max_length=250, null=True)
    image = ResizedImageField(upload_to=slugify_upload, null=True)
    gender = models.CharField(max_length=30, choices=(
        ("Erkak", "Erkak"),
        ("Ayol", "Ayol")
    ), null=True, blank=True, default=None)
    description = models.TextField(max_length=5000, null=True, blank=True)
    message = models.TextField(max_length=650, null=True, blank=True)
    status = models.IntegerField(default=1)
    date_of_release = models.DateField(null=True, blank=True)
    reason_of_ban = models.CharField(max_length=500, null=True, blank=True)
    is_top = models.IntegerField(default=0)
    both_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to=slugify_upload)
    cash = models.IntegerField(default=0)
    card_number = models.CharField(max_length=50, null=True, blank=True)
    card_name = models.CharField(max_length=50, null=True, blank=True)
    card_date = models.CharField(max_length=50, null=True, blank=True)
    wallet_number = models.CharField(max_length=20, null=True, blank=True)
    wallet_expire = models.CharField(max_length=5, null=True, blank=True)
    own_ref_code = models.CharField(max_length=255, null=True, blank=True)
    has_course = models.BooleanField(default=False)

    def __str__(self):
        return self.speaker.username or "-"

    def save(self, *args, **kwargs):
        if self.own_ref_code is None:
            while (True):
                ref = generate_ref()
                sp = Speaker.objects.filter(own_ref_code=ref)
                srs = Users.objects.filter(own_ref_code=ref)
                if sp.count() > 0 or srs.count() > 0:
                    continue
                else:
                    self.own_ref_code = ref
                    break
        super(Speaker, self).save(*args, **kwargs)

    @property
    def calculate_cash(self):
        data = {
            'number': self.wallet_number,
            'expire': self.wallet_expire
        }
        try:
            res = wallet_api(data=data, method='wallet.register')
        except:
            return

        if res['status']:
            self.cash = int(res['result']['balance']) / 100
            self.save()

        return self.cash

    class Meta:
        verbose_name = "Spiker"
        verbose_name_plural = "Spikerlar"


class Users(models.Model):
    password = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True, unique=True)
    card_number = models.CharField(
        max_length=20, null=True, blank=True, unique=False)
    card_expire = models.CharField(
        max_length=20, null=True, blank=True, unique=False)
    wallet_number = models.CharField(max_length=20, null=True, blank=True)
    wallet_expire = models.CharField(max_length=5, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to=slugify_upload, null=True, blank=True)
    regdate = models.DateTimeField(auto_now_add=True, blank=True)
    last_sean = models.DateTimeField(null=True, blank=True)
    cash = models.IntegerField(default=0)
    gender = models.CharField(max_length=30, choices=(
        ("Erkak", "Erkak"),
        ("Ayol", "Ayol")
    ), null=True, blank=True, default=None)
    age = models.DateField(null=True, blank=True)
    job = models.CharField(null=True, blank=True, max_length=150)
    bonus = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    parent_ref_code = models.CharField(max_length=255, null=True, blank=True)
    own_ref_code = models.CharField(max_length=255, null=True, blank=True)
    date_of_release = models.DateField(null=True, blank=True)
    reason_of_ban = models.CharField(max_length=500, blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    def __str__(self):
        return self.phone or "-"

    @property
    def get_country_name(self):
        return self.country.name

    @property
    def get_region_name(self):
        return self.region.name

    def save(self, *args, **kwargs):
        if self.first_name != None and self.last_name != None and self.age != None and self.country != None and self.region != None and self.status != 2:
            bon = RegBonus.objects.last()
            if bon is not None:
                summa = bon.summa_full
            else:
                summa = 0
            self.bonus += summa
            self.status = 2
        if not self.pk:
            self.password = make_password(self.password)
            bon = RegBonus.objects.last()
            if bon is not None:
                summa = bon.summa
            else:
                summa = 0
            self.bonus += summa
            self.status = 1
        if self.own_ref_code is None:
            while (True):
                ref = generate_ref()
                sp = Speaker.objects.filter(own_ref_code=ref)
                srs = Users.objects.filter(own_ref_code=ref)
                if sp.count() > 0 or srs.count() > 0:
                    continue
                else:
                    self.own_ref_code = ref
                    break
        super(Users, self).save(*args, **kwargs)

    @property
    def calculate_cash(self):
        data = {
            'number': self.wallet_number,
            'expire': self.wallet_expire
        }
        try:
            res = wallet_api(data=data, method='wallet.register')
        except:
            return

        if res['status']:
            self.cash = int(res['result']['balance']) / 100
            self.save()

        return self.cash

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


class PaymentHistory(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    summa = models.IntegerField(default=0)
    invois = models.IntegerField(default=0)
    payment_id = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.summa)

    class Meta:
        verbose_name = "To'lov tarixi"
        verbose_name_plural = "To'lovlar tarixi"


class CategoryVideo(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to=slugify_upload, null=True, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.name or "-"


class Language(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name or "-"

    class Meta:
        verbose_name = "Til"
        verbose_name_plural = "Tillar"


class CourseTag(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class CourseTrailer(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    is_file = models.BooleanField(default=False)
    video = models.FileField(upload_to=slugify_upload, blank=True, null=True)
    url = models.URLField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title or "-"


class Course(models.Model):
    turi = (
        ('Bepul', 'Bepul'),
        ('Pullik', 'Pullik')
    )
    video_type = (
        ('Youtube', 'Youtube'),
        ('Video', 'Video')
    )
    levels = (
        ('Beginner', 'Beginner'),
        ('Elementary', 'Elementary'),
        ('Intermediate', 'Intermediate')
    )
    author = models.ForeignKey(
        Speaker, on_delete=models.CASCADE, related_name='course_author')
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=5000, null=True, blank=True)
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, default=1, related_name="course_language")
    level = models.CharField(max_length=12, choices=levels, default='Beginner')
    categories = models.ManyToManyField(
        CategoryVideo, related_name="course_categories", blank=True)
    upload_or_youtube = models.CharField(
        choices=video_type, blank=False, default='Youtube', max_length=15)
    image = ResizedImageField(size=[1280, 720], crop=[
                              'middle', 'center'], upload_to=slugify_upload, null=True)
    trailer = models.OneToOneField(
        CourseTrailer, on_delete=models.CASCADE, blank=True, null=True, related_name='course_trailer')
    course_tags = models.ManyToManyField(
        CourseTag, related_name='course_tags', blank=True)
    price = models.IntegerField(default=0)
    has_certificate = models.BooleanField(default=False)
    logo = models.ImageField(null=True, blank=True, upload_to=slugify_upload)

    turi = models.CharField(choices=turi, default='Pullik', max_length=8)
    date = models.DateTimeField(auto_now_add=True)
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    view = models.IntegerField(default=0)
    is_top = models.IntegerField(default=0)
    is_tavsiya = models.IntegerField(default=0)
    is_confirmed = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    reason_of_ban = models.CharField(max_length=500, null=True, blank=True)

    # additional info
    get_from_course = models.TextField(null=True, blank=True)
    for_whom = models.TextField(null=True, blank=True)
    about_course = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name or "-"

    @property
    def detail(self):
        return {
            'get_from_course': self.get_from_course,
            'for_whom': self.for_whom,
            'about_course': self.about_course
        }

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"


class CourseModule(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    course = models.ForeignKey(Course, verbose_name=_(
        "Kurs"), on_delete=models.CASCADE)
    place_number = models.IntegerField(default=0)

    def __str__(self):
        return self.title or "Module"


class WhatYouLearn(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='whatyoulearn', null=True, blank=True)

    def __str__(self):
        return self.title


class RequirementsCourse(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='courserequirements',
                               null=True, blank=True)

    def __str__(self):
        return self.title


class ForWhomCourse(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='forwhom', null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)

    def __str__(self):
        return self.user.phone

    class Meta:
        verbose_name = "Fikr"
        verbose_name_plural = "Fikrlar"


class VideoCourse(models.Model):
    author = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    courseModule = models.ForeignKey(
        CourseModule, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=100, blank=True, null=True)
    video = models.FileField(upload_to=slugify_upload,
                             default=None, blank=True, null=True)
    image = ResizedImageField(size=[1280, 720], crop=[
                              'middle', 'center'], upload_to=slugify_upload, null=True, blank=True)
    description = models.TextField(max_length=5000, blank=True, null=True)
    is_file = models.BooleanField(default=False)
    link = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)
    place_number = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            text = str(self.link).split('.be/')
            txt = text[0] + 'be.com/embed/' + text[1]
        except:
            txt = None
        self.link = txt
        super(VideoCourse, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videolar"


class CommentCourse(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=5000)


class File(models.Model):
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to=slugify_upload, default=None)
    courseModule = models.ForeignKey(CourseModule, on_delete=models.CASCADE,
                                     blank=True, null=True)
    place_number = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class IsFinished(models.Model):
    from quiz.models import Quiz
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    video = models.ForeignKey(
        VideoCourse, on_delete=models.CASCADE, null=True, blank=True)
    file = models.ForeignKey(
        File, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, null=True, blank=True)
    courseModule = models.ForeignKey(
        CourseModule, on_delete=models.CASCADE, null=True, blank=True)

    finished_at = models.DateTimeField(auto_now_add=True)


class LikeOrDislike(models.Model):
    Up = 1
    Down = -1
    VALUE_CHOICE = (
        (Up, 'Like'),
        (Down, 'Dislike')
    )
    value = models.SmallIntegerField(choices=VALUE_CHOICE, default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    video = models.ForeignKey(VideoCourse, on_delete=models.CASCADE)
    voted_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')


class Rank(models.Model):
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    ranked_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('speaker', 'user')


class VideoViews(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    video = models.ForeignKey(VideoCourse, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')


class TopCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.course.name


class EduonTafsiyasi(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.course.name


class FavoriteCourse(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'course')


class RankCourse(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    speaker_value = models.IntegerField(default=0)
    course_value = models.IntegerField(default=0)
    content_value = models.IntegerField(default=0)
    video_value = models.IntegerField(default=0)

    class Meta:
        unique_together = ('course', 'user')


class Order(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    summa = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    sp_summa = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    for_eduon = models.IntegerField(default=0)
    card_number = models.CharField(max_length=20, default=None, null=True)
    date = models.DateTimeField(auto_now_add=True)


class Billing(models.Model):
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    summa = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    date_req = models.DateTimeField(auto_now_add=True)
    date_pay = models.DateTimeField(auto_now=True)


class ContractWithSpeaker(models.Model):
    eduon = models.IntegerField(default=0)


class OrderPayment(models.Model):
    type_status = (
        (1, "Yaratildi"),
        (2, "To'landi"),
        (3, "Bekor qilindi"),
    )
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    type = models.CharField(max_length=50, choices=(
        ("Click", "Click"), ("PayMe", "PayMe")), null=True, blank=True)
    status = models.IntegerField(default=0, choices=type_status)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return self.user.first_name + " " + self.user.last_name
        except:
            return "-"


class AboutUsNote(models.Model):
    """
    About Us bolimidagi izoh qoldiradigan qism uchun model
    """
    name = models.CharField(max_length=250)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    is_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "-"
