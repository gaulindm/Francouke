from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        UserPreference.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_preference(sender, instance, **kwargs):
    instance.userpreference.save()

class Profile(models.Model):
        #user = models.OntonOneField(User, on_delete=models.CASCADE)
        # Opted to not have pics on FrancoUKe but keeping Profile class for future implementation of bio
        # part 8: https://www.youtube.com/watch?v=FdVuKt_iuSI
        #image = models.ImageField(default='default.jpg',upload_to='profile_pics')

        def __str__(self):
                return f'{self.username} Profile'
        

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userpreference')
    transpose_value = models.IntegerField(default=0)  # e.g., semitone adjustments
    font_size = models.CharField(max_length=5, default="14px")
    line_spacing = models.FloatField(default=1.2)
    text_color = models.CharField(max_length=7, default="#000000")  # Hex color
    chord_color = models.CharField(max_length=7, default="#FF0000")  # Hex color
    chord_weight = models.CharField(max_length=10, default="normal")
    instrument = models.CharField(
           max_length=20,
            choices=[
            ("guitar", "Guitar"),
            ("ukulele", "Ukulele"),
            ("baritone_ukulele", "Baritone Ukulele"),
            ("banjo", "Banjo"),
            ("mandolin", "Mandolin"),
        ],        
           default="ukulele")
    is_lefty = models.BooleanField(default=False)
    chord_diagram_position = models.CharField(max_length=10, default="bottom")
    chord_placement = models.CharField(max_length=20, default="inline")
    # New field
    is_printing_alternate_chord = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.instrument} - Lefty: {self.is_lefty}, Alt Chords: {self.is_printing_alternate_chord}"