from django.contrib import admin
import json
import requests

from django.template.response import TemplateResponse
from .models import *
from django.urls import path
from uniredpay import uniredpay_conf


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'summa')

    def get_urls(self):
        urls = super().get_urls()
        url_patterns = [
            path('get_financial_statistics/',
                 self.admin_site.admin_view(self.account_balance))
        ]
        return url_patterns + urls
    
    def account_balance(self, request):
        res = uniredpay_conf.get_token()

        if res['status']:

            access_token = res['result']['access_token']
            headers = {
                'Unisoft-Authorization': f'Bearer {access_token}',
                'Content-type': 'application/json',
                'Accept': 'Application/json',
                'token': access_token
            }

            d = {
                "jsonrpc": "2.0",
                "id": "{{$randomUUID}}",
                "method": "account.balance",
                "params": {
                }
            }

            req = requests.post(uniredpay_conf.BASE_URL, headers=headers, data=json.dumps(d))

            
            if req.status_code == 200:
                context = dict(
                    self.admin_site.each_context(request),
                    speaker_money=str(req.json()['result']['balance']) + " so'm"
                )
                return TemplateResponse(request, "admin/statistics.html", context)
            else:
                context = dict(
                    self.admin_site.each_context(request),
                    speaker_money="Xatolik"
                )
                return TemplateResponse(request, "admin/statistics.html", context)
        else:
            context = dict(
                self.admin_site.each_context(request),
                speaker_money="Unired hisobiga kirishda xatolik yuzberdi"
            )
            return TemplateResponse(request, "admin/statistics.html", "salom")


admin.site.register(ContractWithSpeaker)
admin.site.register(Billing)
admin.site.register(CommentCourse)
admin.site.register(CourseTag)
admin.site.register(CourseTrailer)
admin.site.register(WhatYouLearn)
admin.site.register(RequirementsCourse)
admin.site.register(ForWhomCourse)
admin.site.register(Module)


@admin.register(VideoCourse)
class VideoCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'date', 'video', 'link')
    list_max_show_all = 50
    list_filter = ('course',)
    search_fields = ('title',)
    date_hierarchy = ('date')


admin.site.register(Permissions)


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'status')
    list_max_show_all = 50
    list_filter = ('type',)
    search_fields = ('user__first_name', 'user__last_name')
    date_hierarchy = ('date')


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = (
    'speaker', 'get_first_name', 'get_last_name', 'phone', 'cash', 'get_email', 'get_date_joined', 'image')
    list_filter = ('cash',)
    list_max_show_all = 50
    search_fields = ('speaker__username', 'speaker__first_name')
    readonly_fields = ('cash', 'card_number', 'wallet_number')
    exclude = ('card_date', 'wallet_expire')

    def get_first_name(self, obj):
        return obj.speaker.first_name

    def get_last_name(self, obj):
        return obj.speaker.last_name

    def get_email(self, obj):
        return obj.speaker.email

    def get_date_joined(self, obj):
        return obj.speaker.date_joined


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('course', 'get_first_name', 'get_last_name', 'date')
    list_max_show_all = 50
    search_fields = ('course__name',)

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'cash', 'bonus', 'status', 'email', 'last_sean', 'image')
    list_max_show_all = 50
    search_fields = ('first_name', "phone", "last_name")
    date_hierarchy = ('regdate')
    readonly_fields = ('cash', 'bonus', 'card_number', 'wallet_number')
    exclude = ('wallet_expire', 'card_expire')


@admin.register(LikeOrDislike)
class LikeOrDislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'video', 'voted_date')
    list_max_show_all = 50
    search_fields = ('user__first_name', 'video__title')
    date_hierarchy = ('voted_date')


@admin.register(CategoryVideo)
class CategoryVideoAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(TopCourse)
class TopCourseAdmin(admin.ModelAdmin):
    list_display = ('course',)


@admin.register(EduonTafsiyasi)
class EduonTafsiyasiAdmin(admin.ModelAdmin):
    list_display = ('course',)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('user', 'speaker', 'value', 'ranked_date')
    list_max_show_all = 50
    search_fields = ('user__first_name', 'speaker__first_name')
    date_hierarchy = ('ranked_date')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'turi', 'date')
    list_max_show_all = 50
    search_fields = ('name',)
    date_hierarchy = ('date')


@admin.register(VideoViews)
class VideoViewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'date')
    list_max_show_all = 50
    date_hierarchy = ('date')


admin.site.register(Info)
admin.site.register(RegBonus)
admin.site.register(ServiceContent)
admin.site.register(ServiceInfo)
admin.site.register(InfoWidget)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(FavoriteCourse)
admin.site.register(Language)
admin.site.register(RankCourse)
