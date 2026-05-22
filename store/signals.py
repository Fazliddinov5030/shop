from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import Wishlist


@receiver(post_save, sender=CustomUser)
def create_user_wishlist(sender, instance, created, **kwargs):
    """Create a wishlist when a new user is created"""
    if created:
        Wishlist.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_wishlist(sender, instance, **kwargs):
    """Save the user's wishlist (if it exists)"""
    if hasattr(instance, 'wishlist'):
        instance.wishlist.save()
