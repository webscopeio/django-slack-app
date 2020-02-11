import json
from typing import Tuple

import slack
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .exceptions import SlackAppNotInstalledProperlyException, SlackAccountNotLinkedException
from .models import SlackWorkspace, SlackUserMapping
from .decorators import slack_verify_request
from .settings import SLACK_LOGIN_OAUTH_REDIRECT_URL, SLACK_INSTALL_OAUTH_REDIRECT_URL
from .helpers import create_workspace_from_oauth2_response, slack_interactivity_callbacks, slack_commands


@login_required  # we make sure user is logged-in in order to link Slack
@require_http_methods(["GET"])  # GET is what Slack invokes, let's forbid others just to be sure
@transaction.atomic  # whatever happens in a db, let's behave atomically
@slack_verify_request
def slack_oauthcallback(request):
    if "error" in request.GET:
        return HttpResponseRedirect(SLACK_INSTALL_OAUTH_REDIRECT_URL)  # TODO - pass GET params

    code = request.GET.get("code")

    client = slack.WebClient(token="")

    response = client.oauth_v2_access(
        client_id=settings.SLACK_CLIENT_ID,
        client_secret=settings.SLACK_CLIENT_SECRET,
        code=code
    )

    workspace, hook = create_workspace_from_oauth2_response(request.user, response.data)

    return HttpResponseRedirect(SLACK_INSTALL_OAUTH_REDIRECT_URL)  # TODO - pass workspace & hook id parameters


@require_http_methods(["GET"])  # GET is what SEND invokes, let's forbid others just to be sure
@slack_verify_request
def slack_login_callback(request):
    if "error" in request.GET:
        return render(SLACK_LOGIN_OAUTH_REDIRECT_URL)  # TODO - pass GET params

    code = request.GET["code"]

    user = authenticate(
        request,
        code=code,
        redirect_uri=request.build_absolute_uri(reverse("slack_app:login"))
    )

    if user is not None:
        login(request, user)

    return HttpResponseRedirect(SLACK_LOGIN_OAUTH_REDIRECT_URL)


@slack_verify_request
@require_http_methods(["POST"])
def slack_interactivity(request):
    payload = json.loads(request.POST.get('payload'))
    fn, required_linked_account = slack_interactivity_callbacks.get(payload.get('type'), None)
    if fn:
        if required_linked_account:
            try:
                workspace, mapping = get_slack_user_and_workspace(
                    request.POST.get('team_id'),
                    request.POST.get('user_id')
                )
            except SlackAppNotInstalledProperlyException:
                return JsonResponse({
                    "text": "Slack application is not linked to your workspace. " +
                            "Please ask your administrators to finish the installation."
                })
            except SlackAccountNotLinkedException as err:
                url = reverse('slack_app:connect_account', kwargs={'nonce': err.slack_user_mapping.nonce})
                return JsonResponse({
                    "text": "Hi, it seems like you haven't linked your Slack account to your Scrumie account. " +
                            f"You can do so <{request.build_absolute_uri(url)}|here>"
                })
        else:
            mapping = None
            workspace = None
        return fn(payload, mapping, workspace)

    return HttpResponse(status=400)


def get_slack_user_and_workspace(team_id, user_id) -> Tuple[SlackUserMapping, SlackWorkspace]:
    try:
        workspace = SlackWorkspace.objects.get(id=team_id)
    except SlackWorkspace.DoesNotExist:
        raise SlackAppNotInstalledProperlyException("Application is not installed properly")

    mapping, created = SlackUserMapping.objects.get_or_create(slack_user_id=user_id, slack_workspace=workspace)

    if created or mapping.user is None:
        raise SlackAccountNotLinkedException(mapping)

    return mapping, workspace


@slack_verify_request
@require_http_methods(["POST"])
def slack_command(request, name: str):
    payload = request.POST
    fn, required_linked_account = slack_commands.get(name, None)
    if fn:
        if required_linked_account:
            try:
                workspace, mapping = get_slack_user_and_workspace(
                    request.POST.get('team_id'),
                    request.POST.get('user_id')
                )
            except SlackAppNotInstalledProperlyException:
                return JsonResponse({
                    "text": "Slack application is not linked to your workspace. " +
                            "Please ask your administrators to finish the installation."
                })
            except SlackAccountNotLinkedException as err:
                url = reverse('slack_app:connect_account', kwargs={'nonce': err.slack_user_mapping.nonce})
                return JsonResponse({
                    "text": "Hi, it seems like you haven't linked your Slack account to your Scrumie account. " +
                            f"You can do so <{request.build_absolute_uri(url)}|here>"
                })
        else:
            workspace = None
            mapping = None

        return fn(payload, mapping, workspace)

    return HttpResponse(status=400)


@login_required
def connect_account(request, nonce: str):
    mapping = get_object_or_404(SlackUserMapping, nonce=nonce)
    mapping.user = request.user
    mapping.save()

    # TODO - allow to specify a function that accepts request, mapping & user and return whatever it wants
    # (Redirect/Render, etc)
    return render(request, "verified_nonce.html")
