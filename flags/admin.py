from django.contrib import admin
from flags.models import Flag

class FlagAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'content_object', 'flagged_by','flag_choice','flag_status')

admin.site.register(Flag, FlagAdmin)
