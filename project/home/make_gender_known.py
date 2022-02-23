from home.models import *

def make_gender_known():
    users = Users.objects.filter(gender=None)
    users.update(gender="Erkak")
    return users.count()