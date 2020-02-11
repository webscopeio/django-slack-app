import datetime
import hashlib
import hmac
import time
from typing import Tuple

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from .models import SlackWorkspace, SlackWebHook, SlackUserMapping

slack_interactivity_callbacks = dict()
slack_commands = dict()


def create_workspace_from_oauth2_response(request_user, response) -> Tuple[SlackWorkspace, SlackWebHook]:
    workspace, created = SlackWorkspace.objects.update_or_create(
        id=response.get("team").get("id"),
        defaults={
            "name": response.get("team").get("name"),
            "bot_access_token": response.get("access_token"),
            "bot_user_id": response.get("bot_user_id"),
            "last_changed": datetime.datetime.now(),
            "response": response,
            "scope": response.get("scope"),
        }
    )

    workspace.update_slack_metadata()

    SlackUserMapping.objects.filter(slack_team_id=workspace.id).update(slack_workspace=workspace)
    workspace.owners.add(request_user)
    webhook_data = response.get("incoming_webhook")

    hook = SlackWebHook.objects.create(
        workspace=workspace,
        channel_id=webhook_data.get("channel_id"),
        channel_name=webhook_data.get("channel"),
        configuration_url=webhook_data.get("configuration_url"),
        url=webhook_data.get("url"),
    )

    return workspace, hook


def is_verified_slack_request(request: HttpRequest) -> bool:
    """
    Implements Slack signature verification according to
    https://api.slack.com/docs/verifying-requests-from-slack

    :param request: Django request
    :return: True if request is verified, False otherwise
    """
    try:
        slack_signing_secret = settings.SLACK_SIGNING_SECRET
    except AttributeError:
        raise ImproperlyConfigured(
            "SLACK_SIGNING_SECRET is missing in your settings.py" +
            "Please check the readme of django-slack-integration package"
        )

    slack_signature = request.META.get('HTTP_X_SLACK_SIGNATURE')
    slack_request_timestamp = request.META.get('HTTP_X_SLACK_REQUEST_TIMESTAMP')

    if not slack_signature or not slack_request_timestamp:
        return False

    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return False

    sig_basestring = f"v0:{slack_request_timestamp}:{request.body.decode('utf-8')}".encode("utf-8")
    my_signature = 'v0=' + hmac.new(bytes(slack_signing_secret, 'utf-8'), sig_basestring, hashlib.sha256).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)
