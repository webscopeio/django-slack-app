from django.conf import settings

SLACK_LOGIN_OAUTH_REDIRECT_URL = getattr(settings, 'SLACK_LOGIN_OAUTH_REDIRECT_URL', "/")
SLACK_INSTALL_OAUTH_REDIRECT_URL = getattr(settings, 'SLACK_INSTALL_OAUTH_REDIRECT_URL', "/")
