from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TokenBlacklistConfig(AppConfig):
    name = 'simplejwt.token_blacklist'
    verbose_name = _('Token Blacklist')
