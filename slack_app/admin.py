from django.contrib import admin
from .models import SlackWorkspace, SlackUserMapping

admin.site.register(SlackWorkspace)
admin.site.register(SlackUserMapping)
