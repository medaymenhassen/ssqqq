from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
# from .models import UserProfile  # Now we'll create a Django-specific model for this


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(
            user=instance,
            firstname=instance.first_name or '',
            lastname=instance.last_name or '',
            role='USER',
            enabled=True,
            account_non_expired=True,
            account_non_locked=True,
            credentials_non_expired=True
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when a User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()