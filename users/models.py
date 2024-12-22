from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
        #user = models.OntonOneField(User, on_delete=models.CASCADE)
        # Opted to not have pics on FrancoUKe but keeping Profile class for future implementation of bio
        # part 8: https://www.youtube.com/watch?v=FdVuKt_iuSI
        #image = models.ImageField(default='default.jpg',upload_to='profile_pics')

        def __str__(self):
                return f'{self.username} Profile'
        
