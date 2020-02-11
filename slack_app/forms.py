from django import forms


class SlackCommandForm(forms.Form):
    token = forms.CharField()
    command = forms.CharField()

    team_id = forms.CharField(required=False)
    team_domain = forms.CharField(required=False)

    channel_id = forms.CharField(required=False)
    channel_name = forms.CharField(required=False)

    user_id = forms.CharField()
    user_name = forms.CharField()

    response_url = forms.URLField()
    trigger_id = forms.CharField()

    enterprise_id = forms.CharField(required=False)
    enterprise_name = forms.CharField(required=False)
