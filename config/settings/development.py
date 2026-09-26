"""
MwohaOS Development Settings
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Use standard static files storage during development without strict manifest requirement
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Internal IPs for debug toolbar or local tools if needed
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Email backend: console for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
