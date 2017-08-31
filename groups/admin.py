from django.contrib import admin

from groups.models import GroupProfile, PendingMember

admin.site.register(GroupProfile)
admin.site.register(PendingMember)