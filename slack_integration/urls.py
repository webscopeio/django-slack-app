from django.urls import path

from .views import slack_oauthcallback, slack_login_callback

urlpatterns = [
    path('install/', slack_oauthcallback, name='install'),
    path('login/', slack_login_callback, name='login'),
]