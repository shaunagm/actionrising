from django.contrib import admin

from profiles.models import (Profile, Relationship, ProfileActionRelationship,
    ProfileSlateRelationship, PrivacyDefaults, NavbarSettings)

admin.site.register(Profile)
admin.site.register(Relationship)
admin.site.register(ProfileActionRelationship)
admin.site.register(ProfileSlateRelationship)
admin.site.register(PrivacyDefaults)
admin.site.register(NavbarSettings)
