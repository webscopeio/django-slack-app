from functools import wraps

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from slack_integration.forms import SlackCommandForm

from .helpers import is_verified_slack_request

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


def slack_verify_request(view_func):
    def wrapped_view(request, *args, **kwargs):
        if is_verified_slack_request(request):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest("Slack signature verification failed")

    return wraps(view_func)(wrapped_view)


def slack_command(view_func):
    @csrf_exempt
    @slack_verify_request  # all slack commands must be verified
    @require_http_methods(["POST"])
    def wrapped_view(request, *args, **kwargs):
        form = SlackCommandForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid request')

        team_id = form.cleaned_data.get('team_id')
        user_id = form.cleaned_data.get('user_id')

        workspace = SlackWorkspace.objects.get(id=team_id)
        slack_user_mapping = SlackUserMapping.objects.get(slack_user_id=user_id)

        return view_func(request, slack_user_mapping=slack_user_mapping, slack_workspace=workspace, *args, **kwargs)

    return wraps(view_func)(wrapped_view)


def slack_command_simple(view_func):
    @csrf_exempt
    @slack_verify_request  # all slack commands must be verified
    @require_http_methods(["POST"])
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wraps(view_func)(wrapped_view)