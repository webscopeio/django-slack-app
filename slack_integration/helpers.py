import datetime
from typing import Tuple

from .models import SlackWorkspace, SlackWebHook, SlackUserMapping


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
