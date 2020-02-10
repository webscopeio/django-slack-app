from django.urls import path

from .views import slack_oauthcallback, slack_login_callback, slack_interactivity

urlpatterns = [
    path('install/', slack_oauthcallback, name='install'),
    path('login/', slack_login_callback, name='login'),
    path('interactivity/', slack_interactivity, name='interactivity'),
]