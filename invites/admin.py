from django.contrib import admin
from invites.models import Invite

class InviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'request_status', 'initial_request_date')
admin.site.register(Invite, InviteAdmin)
