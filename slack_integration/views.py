import json

import slack
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .decorators import slack_verify_request
from .settings import SLACK_LOGIN_OAUTH_REDIRECT_URL, SLACK_INSTALL_OAUTH_REDIRECT_URL
from .helpers import create_workspace_from_oauth2_response, slack_interactivity_callbacks


@login_required  # we make sure user is logged-in in order to link Slack
@require_http_methods(["GET"])  # GET is what Slack invokes, let's forbid others just to be sure
@transaction.atomic  # whatever happens in a db, let's behave atomically
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
def slack_login_callback(request):
    if "error" in request.GET:
        return render(SLACK_LOGIN_OAUTH_REDIRECT_URL)  # TODO - pass GET params

    code = request.GET["code"]

    user = authenticate(
        request,
        code=code,
        redirect_uri=request.build_absolute_uri(reverse("slack_integration:login"))
    )

    if user is not None:
        login(request, user)

    return HttpResponseRedirect(SLACK_LOGIN_OAUTH_REDIRECT_URL)


@csrf_exempt
@slack_verify_request
@require_http_methods(["POST"])
def slack_interactivity(request):
    payload = json.loads(request.POST.get('payload'))
    fn = slack_interactivity_callbacks.get(payload.get('type'), None)
    if fn:
        return fn(payload)

    return HttpResponse(status=400)
