from rest_framework.response import Response

from home.models import Users
from simplejwt.backends import TokenBackend


def get_user_id(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
    except:
        return None

    return valid_data['user_id']
