import slack
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db import transaction

from .models import SlackUserMapping, SlackWorkspace

User = get_user_model()


class SlackAuthenticationBackend(BaseBackend):

    @transaction.atomic
    def authenticate(self, request, code=None, redirect_uri=None, *args, **kwargs):
        if code is None:
            return None

        client = slack.WebClient(token="")

        response = client.oauth_access(
            client_id=settings.SLACK_CLIENT_ID,
            client_secret=settings.SLACK_CLIENT_SECRET,
            code=code,
            redirect_uri=redirect_uri
        )

        data = response.data

        if not data.get("ok"):
            return None

        user_id = data.get("user_id")

        try:
            slack_workspace = SlackWorkspace.objects.get(id=data.get("team_id"))
        except SlackWorkspace.DoesNotExist:
            slack_workspace = None

        slack_user, created = SlackUserMapping.objects.update_or_create(
            slack_user_id=user_id,
            defaults={
                "access_token": data.get("access_token"),
                "slack_team_id": data.get("team_id"),
                "slack_workspace": slack_workspace,  # shortcut for each access, on_delete=models.SET_NULL
            }
        )

        if slack_user.user is None:
            username = data.get("user").get("name")
            # TODO get an unique username in a more sophisticated way
            n = 1
            while User.objects.filter(username=username).exists():
                username = f"{data.get('user').get('name')}-{n}"
                n += 1

            user = User.objects.create(username=username)

            slack_user.user = user
            slack_user.save()

        return slack_user.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
