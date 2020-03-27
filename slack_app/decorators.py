from functools import wraps

import slack
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest

from .signals import slack_event_received, refresh_home
from .models import SlackUserMapping, SlackWorkspace

from .helpers import is_verified_slack_request, slack_interactivity_callbacks, slack_commands


def slack_command(name, require_linked_account=True):
    def _decorator(handler_func):
        if slack_commands.get(name, None):
            raise ImproperlyConfigured(f"You are trying to connect one slash command to multiple functions.")
        slack_commands[name] = (handler_func, require_linked_account)
        return handler_func

    return _decorator


def slack_interactivity(interactivity_type, require_linked_account=True):
    def _decorator(handler_func):
        if slack_interactivity_callbacks.get(interactivity_type, None):
            raise ImproperlyConfigured(f"You are trying to connect '{interactivity_type}' in multiple functions.")
        slack_interactivity_callbacks[interactivity_type] = (handler_func, require_linked_account)
        return handler_func

    return _decorator


def slack_verify_request(view_func):
    def wrapped_view(request, *args, **kwargs):
        if is_verified_slack_request(request):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest("Slack signature verification failed")

    # we verify that the request is coming from Slack, csrf is irrelevant, but most importantly not provided at all
    view_func.csrf_exempt = True

    return wraps(view_func)(wrapped_view)


def on_slack_signal(*event_types, inject_slack_models=False):
    def decorator_receiver(receiver_func):
        @wraps(receiver_func)
        def signal_receiver(sender, event_type, event_data, signal, **kwargs):
            if event_type in event_types:
                try:
                    slack_user_mapping = SlackUserMapping.objects.get(pk=event_data.get('user'))
                except SlackUserMapping.DoesNotExist:
                    slack_user_mapping = None

                try:
                    slack_workspace = SlackWorkspace.objects.get(pk=kwargs.get('team_id'))
                except SlackWorkspace.DoesNotExist:
                    slack_workspace = None

                slack_models = {
                    "slack_user_mapping": slack_user_mapping,
                    "slack_workspace": slack_workspace,
                } if inject_slack_models else {}
                return receiver_func(sender, event_data=event_data, event_type=event_type, **slack_models, **kwargs)

        slack_event_received.connect(signal_receiver, weak=False)

    return decorator_receiver


def slack_app_home(receiver_func):
    @wraps(receiver_func)
    def signal_receiver(
        sender,
        event_type=None,
        event_data=None,

        slack_user_mapping=None,
        slack_workspace=None,
        **kwargs
    ):
        if event_type == 'app_home_opened':
            slack_user_mapping = SlackUserMapping.objects.get(pk=event_data.get('user'))
            slack_workspace = SlackWorkspace.objects.get(pk=kwargs.get('team_id'))

        blocks, title = receiver_func(
            sender,
            event_data=event_data,
            event_type=event_type,
            slack_user_mapping=slack_user_mapping,
            slack_workspace=slack_workspace,
            **kwargs,
        )

        client = slack.WebClient(token=slack_workspace.bot_access_token)
        client.views_publish(user_id=slack_user_mapping.slack_user_id, view={
            "type": 'home',
            "title": title,
            "blocks": blocks
        })

    slack_event_received.connect(signal_receiver, weak=False)
    refresh_home.connect(signal_receiver, weak=False)

    return signal_receiver
