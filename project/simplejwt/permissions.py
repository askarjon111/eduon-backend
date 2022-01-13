from rest_framework import permissions
from home.models import Users

class JwtPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        try:
            user = Users.objects.get(id=request.user.id)
            if user is not None:
                return True
            else:
                return False
        except:
            return False