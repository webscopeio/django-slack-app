
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
    
6. Add following URLs to your Slack app's Redirect URLs (OAuth & Permissions)

   ```
   <your_host>/slack/oauthcallback/
   <your_host>/slack/login/
   ```
   
7. (Optional) Put `<your_host>/slack/interactivity/` as your Request URL in `Interactive Components` section

8. (Optional) Configure your Slash commands's Request URL as `<your_host>/slack/commands/<command_name>/`
   
## Usage

### Slack commands

If you want to create a new Slack command with name `/example`, configure your Request URL as `<your_host>/slack/commands/example/` and put the following code into `slack.py` inside your app's directory.

```python
@slack_command('example', require_linked_account=True)
def scrumie_staging_command(request, slack_user_mapping, slack_workspace):
    print(slack_user_mapping, slack_workspace)
    return JsonResponse({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello _world_"
                },
            }
        ],
        "text": "Hello World"
    })
```

### Slack Interactivity

Put the following to your `slack.py` inside your app's directory.

```python
@slack_interactivity('block_actions')
def process_block_actions(payload):
    print('>>>>', payload)
    return HttpResponse()
```
