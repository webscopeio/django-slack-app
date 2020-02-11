
# Django Slack Integration

This application helps you to integrate your existing Django application with Slack.

It provides you with

- Models - needed to keep information from Slack API
- Decorators - help you to write implementation of your Slack endpoints
- Authorisation backend - allows you to pair your existing user model with your Slack users
- Views - OAuth callbacks for "Add To Slack" and "Login With Slack" actions

## Installation

1. Add 'slack_app' to your INSTALLED_APPS setting like this:

    ```python
    INSTALLED_APPS = [
        ...
        'slack_app',
        ...
    ]
    ```

2. Include the urls in your project `urls.py` like this:

    ```
    path('slack/', include('slack_app.urls')),
    ```

3. Run `python manage.py migrate` to create the `slack_app` models.

4. Add `slack_app.auth_backends.SlackAuthenticationBackend` to your `AUTHENTICATION_BACKENDS`

    ```python
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'slack_app.auth_backends.SlackAuthenticationBackend',
    ]
    ```

5. Update your `settings.py`

    ```python
    SLACK_CLIENT_ID=""
    SLACK_CLIENT_SECRET=""
    SLACK_SIGNING_SECRET=""
    
    SLACK_LOGIN_OAUTH_REDIRECT_URL=""
    SLACK_INSTALL_OAUTH_REDIRECT_URL=""
    ```