from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm
from django import forms
from home.models import Speaker
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class FormChangePassword(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1']

# class RegisterFullForm(Form):
#
#     def clean_phone(self):
#         phone = self.cleaned_data['phone']
#         if Speaker.objects.filter(phone=phone).exists():
#             raise ValidationError("This phone number is already registered!")
#         return phone
#
#     class Meta:
#         model = Speaker
#         fields = [
#             'phone',
#             'kasbi',
#             'phone',
#             'description',
#             'message',
#         ]
