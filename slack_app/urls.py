from django.urls import path

from .views import slack_oauthcallback, slack_login_callback, slack_interactivity, slack_command, connect_account

app_name = "slack_app"

urlpatterns = [
    path('install/', slack_oauthcallback, name='install'),
    path('login/', slack_login_callback, name='login'),
    path('interactivity/', slack_interactivity, name='interactivity'),
    path('commands/<str:name>/', slack_command, name='command'),
    path('connect/<str:nonce>/', connect_account, name='connect_account'),
]