import uuid
import slack

from django.conf import settings
from django.contrib.auth import get_user_model, user_logged_in
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from slack.errors import SlackApiError

User = get_user_model()


class SlackWorkspace(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    scope = models.CharField(max_length=1024)
    bot_access_token = models.CharField(max_length=255)
    bot_user_id = models.CharField(max_length=255)
    last_changed = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    response = JSONField()

    owners = models.ManyToManyField(User, related_name='owned_slack_workspaces')

    domain = models.CharField(max_length=255, null=True)
    image_34 = models.URLField(null=True)
    image_44 = models.URLField(null=True)
    image_68 = models.URLField(null=True)
    image_88 = models.URLField(null=True)
    image_102 = models.URLField(null=True)
    image_132 = models.URLField(null=True)
    image_230 = models.URLField(null=True)
    image_original = models.URLField(null=True)
    image_default = models.BooleanField(null=True)

    enterprise_id = models.CharField(max_length=128, null=True)
    enterprise_name = models.CharField(max_length=128, null=True)

    def get_bot_scopes(self):
        return self.scope.split(',') if self.scope else []

    def update_slack_metadata(self):
        """
        Called to re-fetch data about this entity from Slack API
        :return:
        """
        client = slack.WebClient(token=self.bot_access_token)
        res = client.team_info()

        if res.get('ok'):
            team_data = res.get("team")

            self.name = team_data.get("name")
            self.domain = team_data.get("domain")
            self.email_domain = team_data.get("email_domain")
            self.enterprise_id = team_data.get("enterprise_id")
            self.enterprise_name = team_data.get("enterprise_name")
            self.image_34 = team_data.get("icon").get("image_34")
            self.image_44 = team_data.get("icon").get("image_44")
            self.image_68 = team_data.get("icon").get("image_68")
            self.image_88 = team_data.get("icon").get("image_88")
            self.image_102 = team_data.get("icon").get("image_102")
            self.image_132 = team_data.get("icon").get("image_132")
            self.image_230 = team_data.get("icon").get("image_230")
            self.image_original = team_data.get("icon").get("image_original")
            self.image_default = team_data.get("icon").get("image_default", False)
            self.save()

    def __str__(self):
        return self.name


class SlackWebHook(models.Model):
    workspace = models.ForeignKey(SlackWorkspace, on_delete=models.CASCADE, related_name='webhooks')
    channel_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    configuration_url = models.URLField(max_length=255)
    url = models.URLField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.channel_name}@{self.workspace.name}"


class SlackUserMapping(models.Model):
    slack_user_id = models.CharField(max_length=255, db_index=True, primary_key=True)
    slack_team_id = models.CharField(max_length=255)

    # user can be null till it's unassigned
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='slack_accounts')

    # If slack app is uninstalled, all of the tokens are uninstalled as well
    slack_workspace = models.ForeignKey(SlackWorkspace, on_delete=models.CASCADE, related_name='slack_users', null=True)

    access_token = models.CharField(max_length=255)
    nonce = models.UUIDField(max_length=36, default=uuid.uuid4)

    slack_email = models.EmailField(null=True)
    image_24 = models.URLField(null=True)
    image_32 = models.URLField(null=True)
    image_48 = models.URLField(null=True)
    image_72 = models.URLField(null=True)
    image_192 = models.URLField(null=True)
    image_512 = models.URLField(null=True)
    image_1024 = models.URLField(null=True)

    workspace_name = models.CharField(max_length=255)
    workspace_domain = models.CharField(max_length=255)
    workspace_image_34 = models.URLField(null=True)
    workspace_image_44 = models.URLField(null=True)
    workspace_image_68 = models.URLField(null=True)
    workspace_image_88 = models.URLField(null=True)
    workspace_image_102 = models.URLField(null=True)
    workspace_image_132 = models.URLField(null=True)
    workspace_image_230 = models.URLField(null=True)
    workspace_image_original = models.URLField(null=True)

    def update_slack_metadata(self):
        """
        Called to re-fetch data about this entity from Slack API
        :return:
        """
        client = slack.WebClient(token=self.access_token)
        res = client.users_identity()

        if res.get('ok'):
            user_data = res.get("user")
            team_data = res.get("team")

            self.name = user_data.get("name")
            self.slack_email = user_data.get("email")

            self.image_24 = user_data.get("image_24")
            self.image_32 = user_data.get("image_32")
            self.image_48 = user_data.get("image_48")
            self.image_72 = user_data.get("image_72")
            self.image_192 = user_data.get("image_192")
            self.image_512 = user_data.get("image_512")
            self.image_1024 = user_data.get("image_1024")

            self.workspace_name = team_data.get("name")
            self.workspace_domain = team_data.get("domain")
            self.workspace_image_34 = team_data.get("image_34")
            self.workspace_image_44 = team_data.get("image_44")
            self.workspace_image_68 = team_data.get("image_68")
            self.workspace_image_88 = team_data.get("image_88")
            self.workspace_image_102 = team_data.get("image_102")
            self.workspace_image_132 = team_data.get("image_132")
            self.workspace_image_230 = team_data.get("image_230")
            self.workspace_image_original = team_data.get("image_original")

            self.save()

    def __str__(self):
        username = self.user.username if self.user else 'Unassigned Account'
        return username


@receiver(pre_delete, sender=SlackWorkspace)
def post_delete_slack_workspace(instance, *args, **kwargs):
    """
    Once the application is removed from Django, let's remove it from Slack's workspace
    """
    client = slack.WebClient(token=instance.bot_access_token)
    try:
        client.api_call('apps.uninstall', params={
            "client_id": settings.SLACK_CLIENT_ID,
            "client_secret": settings.SLACK_CLIENT_SECRET,
        })
    except SlackApiError:
        # for now fail silently
        pass


@receiver(user_logged_in)
def refetch_user_slack_metadata(sender, user, request, **kwargs):
    """
    We will re-fetch user's data after a successful login.
    """
    for slack_user in user.slack_accounts.all():
        slack_user.update_slack_metadata()
