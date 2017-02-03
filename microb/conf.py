# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User


USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', User)

USE_REVERSION=getattr(settings, 'MICROB_USE_REVERSION', "reversion" in settings.INSTALLED_APPS)

DB = getattr(settings, 'MICROB_DB', "microb")
TABLE = getattr(settings, 'MICROB_TABLE', "pages")

CODE_MODE = getattr(settings, 'MICROB_CODE_MODE', False)
CODEMIRROR_KEYMAP = getattr(settings, 'MICROB_CODEMIRROR_KEYMAP', 'default')