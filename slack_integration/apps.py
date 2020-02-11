from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class SlackIntegrationAppConfig(AppConfig):
    name = 'slack_integration'
    verbose_name = 'Slack Integration'

    def ready(self):
        super().ready()

        autodiscover_modules('slack')
