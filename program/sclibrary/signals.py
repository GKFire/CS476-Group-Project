"""Signals: guarantee every Lender owns a Library (Korbin's requirement)."""
from django.db.models.signals import post_save
from django.dispatch import receiver

import sclibrary.models as M


@receiver(post_save, sender=M.Lender)
def create_library_for_new_lender(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "library"):
        M.Library.objects.create(name=f"{instance.username}'s Library", owner=instance)
