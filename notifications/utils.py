def give_old_profiles_new_settings():
    from django.contrib.auth.models import User
    from notifications.models import NotificationSettings
    for user in User.objects.all():
        NotificationSettings.objects.create(user=user)
