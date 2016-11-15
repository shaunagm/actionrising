from django.contrib import admin

from profiles.models import Profile, Relationship, ProfileActionRelationship

admin.site.register(Profile)
admin.site.register(Relationship)
admin.site.register(ProfileActionRelationship)
