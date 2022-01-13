from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views, wallet_view

urlpatterns = [
    path('card-register/', csrf_exempt(views.card_register)),
    path('card-info/', csrf_exempt(views.card_info)),
    path('card-history/', csrf_exempt(views.card_history)),
    path('add-terminal/', csrf_exempt(views.add_terminal)),
    path('remove-terminal/', csrf_exempt(views.remove_terminal)),
    path('check-terminal/', csrf_exempt(views.check_terminal)),

    # hold
    path('hold-create/', csrf_exempt(views.hold_create)),
    path('hold-dismiss/', csrf_exempt(views.hold_dismiss)),
    path('hold-charge/', csrf_exempt(views.hold_charge)),

    # payment
    path('send-sms/', csrf_exempt(views.send_sms_to_user)),
    path('pay-for-balance/', csrf_exempt(views.pay_for_balance)),
    path('pay-for-course-from-balance/', csrf_exempt(views.pay_to_course_from_balance)),
    path('pay-for-course-from-card/', csrf_exempt(views.pay_to_course_from_card)),

    # get money
    path('get-speaker-money/', csrf_exempt(views.get_money_from_wallet)),

    # statistics
    path('get-payment-history/', csrf_exempt(views.get_payment_history)),
    path('get-courses-order-list/', csrf_exempt(views.get_course_orders)),
]

urlpatterns += [
    path('create-online-wallet-for-all/', wallet_view.CreateWalletUserAndSpeakersCLass.as_view()),
    path('create-online-wallet-for-speaker/', wallet_view.CreateOnlineCardForSpeaker.as_view()),
    path('create-online-wallet-for-user/', wallet_view.CreateOnlineCardForUser.as_view()),
]
