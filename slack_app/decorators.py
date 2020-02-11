from functools import wraps

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest

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
