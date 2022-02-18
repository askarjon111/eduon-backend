from datetime import date, timezone
from background_task import background
from home.models import Speaker, Users
from django.db.models import Q


@background(schedule=60)
def release_speaker():
    speaker = Speaker.objects.filter(Q(status=0) & Q(
        date_of_release=date.today()))
    speaker.update(status=1, reason_of_ban='')
    

@background(schedule=60)
def release_user():
    user = Users.objects.filter(Q(is_active=False) & Q(
        date_of_release=date.today()))
    user.update(is_active=True, reason_of_ban='')
