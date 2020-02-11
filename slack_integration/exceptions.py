class SlackAppNotInstalledProperlyException(Exception):
    """
    Thrown if no entry for a Slack app exists in a Django DB.
    """
    pass


class SlackAccountNotLinkedException(Exception):
    """
    Thrown if user is not linked with a User model yet.
    """
    def __init__(self, slack_user_mapping):
        super().__init__()
        self.slack_user_mapping = slack_user_mapping
