import django.dispatch

"""
Slack want us to implement a queue to react to events.
https://api.slack.com/events-api#responding_to_events

That's why, we've chosen to implement this using Django's signals.
"""
slack_event_received = django.dispatch.Signal(providing_args=["event_type", "event_data"])
refresh_home = django.dispatch.Signal(providing_args=["slack_user_mapping", "slack_workspace"])
