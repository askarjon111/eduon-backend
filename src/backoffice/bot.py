# import telebot
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
#
# from .models import TelegramBotUser as UserId
#
# bot = telebot.TeleBot('611644983:AAGh6JNaXeG6xppzvWbwsxpv6RmCwguy3Rg')
#
#
# class EduonBot(APIView):
#     def post(self, request):
#         json_string = request.body.decode('UTF-8')
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return Response({'code': 200})
#
#
# @bot.message_handler(commands=['start'])
# def start(message):
#     # user, created = UserId.objects.get_or_create(pk=message.from_user.id)
#     # user.feedback_img = None
#     # user.feedback = None
#     # user.step = 1
#     # user.save()
#     text = 'Welcome !!!'
#     bot.send_message(message.chat.id, text)

#
# @bot.message_handler(content_types=['text'])
# def text_message(message):
#     user = UserId.objects.get(pk=message.from_user.id)
#     switcher = {
#         0: start,
#         1: first_name,
#         2: last_name,
#         3: phone,
#         4: who_is
#     }
#     func = switcher.get(user.step, lambda: start(message))
#     func(message)
#
#
# def hasNumbers(string):
#     return any(char.isdigit() for char in string)
#
#
# def first_name(message):
#     user = UserId.objects.get(pk=message.from_user.id)
#     if hasNumbers(message.text) or message.text in ['Bilim beruvchi', 'Bilim oluvchi', 'Qiziquvchi']:
#         bot.send_message(message.chat.id, 'Ismingizni to\'g\'ri kiriting!')
#     else:
#         user.first_name = message.text
#         user.step = 2
#         user.save()
#         bot.send_message(message.chat.id, 'Familyangizni kiriting !')
#
#
# def last_name(message):
#     user = UserId.objects.get(pk=message.from_user.id)
#     if hasNumbers(message.text) or message.text in ['Bilim beruvchi', 'Bilim oluvchi', 'Qiziquvchi']:
#         bot.send_message(message.chat.id, 'Familyangizni to\'g\'ri kiriting!')
#     else:
#         user.last_name = message.text
#         user.step = 3
#         user.save()
#         rkm = ReplyKeyboardMarkup(True)
#         rkm.add(KeyboardButton('Nomer yuborish', request_contact=True))
#         bot.send_message(message.chat.id, 'Telefon raqamingizni kiriting! ushbu ko\'rinishda (901234567)',
#                          reply_markup=rkm)
#
#
# @bot.message_handler(content_types=['contact'])
# def text_message(message):
#     user = UserId.objects.get(pk=message.from_user.id)
#     user.phone = message.contact.phone_number
#     user.step = 4
#     user.save()
#     rkm = ReplyKeyboardMarkup(True)
#     rkm.add('Bilim beruvchi')
#     rkm.add('Bilim oluvchi')
#     rkm.add('Qiziquvchi')
#     bot.send_message(message.chat.id, 'Kim tomonidan', reply_markup=rkm)
#
#
# def phone(message):
#     user = UserId.objects.get(pk=message.from_user.id)
#     if message.text.isdigit() and len(message.text) == 9:
#         user.phone = message.text
#         user.step = 4
#         user.save()
#         rkm = ReplyKeyboardMarkup(True)
#         rkm.add('Bilim beruvchi')
#         rkm.add('Bilim oluvchi')
#         rkm.add('Qiziquvchi')
#         bot.send_message(message.chat.id, 'Kim tomonidan', reply_markup=rkm)
#     else:
#         rkm = ReplyKeyboardMarkup(True)
#         rkm.add(KeyboardButton('Nomer yuborish', request_contact=True))
#         bot.send_message(message.chat.id, 'Nomeringizni to\'g\'ri kiriting (901234567)', reply_markup=rkm)
#
#
# def who_is(message):
#     user = UserId.objects.get(pk=message.from_user.id)
#     if message.text in ['Bilim beruvchi', 'Bilim oluvchi', 'Qiziquvchi']:
#         user.who_is = message.text
#         user.step = 5
#         user.save()
#         markup = ReplyKeyboardRemove(selective=False)
#         bot.send_message(message.chat.id, 'Feedback ni yuboring', reply_markup=markup)
#     else:
#         rkm = ReplyKeyboardMarkup(True)
#         rkm.add('Bilim beruvchi')
#         rkm.add('Bilim oluvchi')
#         rkm.add('Qiziquvchi')
#         bot.send_message(message.chat.id, 'Kim tomonidan', reply_markup=rkm)
#
#
# @bot.message_handler(content_types=['photo'])
# def get_feedback_photo(message):
#     user = UserId.objects.get(pk=message.from_user.id)
#     user.feedback_img = message.photo[0].file_id
#     user.save()
