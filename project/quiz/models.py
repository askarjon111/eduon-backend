from django.db import models
from os.path import splitext
from transliterate.utils import _, slugify

from home.models import Module, Users


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


class Quiz(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Quiz Title"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Testlar")
        ordering = ['id']


class Question(models.Model):
    questionText = models.CharField(max_length=255,blank=True, null=True)
    questionImage = models.ImageField(upload_to=slugify_upload)
    result = models.ForeignKey("Result", on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Savol")
        verbose_name_plural = _("Savollar")
        ordering = ['id']


class Answer(models.Model):
    question = models.ForeignKey(
        Question, related_name='answer', on_delete=models.CASCADE)
    answerText = models.CharField(max_length=500, blank=True, null=True)
    answerImage = models.ImageField(upload_to=slugify_upload)
    isCorrect = models.BooleanField(default=False)

class Result(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    quiz = models.ManyToManyField(Quiz, related_name='result')