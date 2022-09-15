import django.dispatch

"""
Slack want us to implement a queue to react to events.
https://api.slack.com/events-api#responding_to_events

That's why, we've chosen to implement this using Django's signals.
"""
slack_event_received = django.dispatch.Signal()
refresh_home = django.dispatch.Signal()
