from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Admin').exists():
            return True
        else:
            return False


class ManagerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists():
            return True
        else:
            return False


class MarketingManagerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Marketing manager').exists():
            return True
        else:
            return False


class OwnerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Owner').exists():
            return True
        else:
            return False
