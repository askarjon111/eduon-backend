from datetime import date, timezone
from background_task import background
from home.models import Speaker, Users
from django.db.models import Q


@background(schedule=60)
def release_speaker():
    speakers = Speaker.objects.filter(Q(status=0) & Q(
        date_of_release=date.today()))
    for speaker in speakers:
        speaker.status = 1
        speaker.reason_of_ban = ''
        speaker.date_of_release=None
        speaker.save()
    # speaker.update(status=1, reason_of_ban='', date_of_release='')
    

@background(schedule=60)
def release_user():
    users = Users.objects.filter(Q(is_active=False) & Q(
        date_of_release=date.today()))
    for user in users:
        user.is_active = True
        user.reason_of_ban = ''
        user.date_of_release = None
        user.save()
    # user.update(is_active=True, reason_of_ban='')
