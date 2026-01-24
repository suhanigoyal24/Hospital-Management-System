from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DoctorProfile, PatientProfile, AvailabilitySlot, Booking
from django.db.models.signals import post_save
from django.dispatch import receiver

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass  # default UserAdmin behavior for superuser/staff login

admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
admin.site.register(AvailabilitySlot)
admin.site.register(Booking)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'doctor':
            DoctorProfile.objects.get_or_create(user=instance)
        elif instance.role == 'patient':
            PatientProfile.objects.get_or_create(user=instance)
