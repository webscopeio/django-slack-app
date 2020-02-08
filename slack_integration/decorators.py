from django.http import JsonResponse
from django.urls import reverse

from .models import SlackWorkspace, SlackUserMapping


def require_linked_slack_account():
    """
    Checks whether user has linked his/her Slack account with User model
    """

    def decorator(custom_method):
        def _decorator(self, *args, **kwargs):
            team_id = self.POST.get('team_id')
            try:
                workspace = SlackWorkspace.objects.get(id=team_id)
            except SlackWorkspace.DoesNotExist:
                return JsonResponse({
                    "text": "Slack application is not linked to your workspace. " +
                            "Please ask your administrators to finish the installation."
                })

            user_id = self.POST.get('user_id')
            mapping, created = SlackUserMapping.objects.get_or_create(slack_user_id=user_id, slack_workspace=workspace)

            if created or mapping.user is None:
                # url = reverse('slack:bind-accounts', kwargs={'nonce': mapping.nonce})
                url = "https://example.com"
                return JsonResponse({
                    "text": "Hi, it seems like you haven't linked your Slack account to your Scrumie account. " +
                            f"You can do so <{self.build_absolute_uri(url)}|here>"
                })

            return custom_method(self, mapping, workspace, *args, **kwargs)

        return _decorator

    return decorator
