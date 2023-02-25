from django.utils.timezone import datetime

def sum2coins(amount):
    return amount * 100


def coin2sums(amount):
    return amount / 100


def time_now_in_ms():
    return int(datetime.now().timestamp()*1000)
