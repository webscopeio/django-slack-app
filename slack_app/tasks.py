from celery import shared_task

from .signals import slack_event_received


@shared_task
def receive_slack_signal_task(sender, event_type, event_data, **data):
    slack_event_received.send(sender=sender, event_type=event_type, event_data=event_data, **data)

