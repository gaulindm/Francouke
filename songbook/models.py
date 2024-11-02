from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Song(models.Model):
    songTitle = models.CharField(max_length=100,blank=True, null=True)
    songChordPro = models.TextField()
    date_posted = models.DateField(default=timezone.now)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.songTitle
    
    def get_absolute_url(self):
        return reverse('song-detail', kwargs={'pk':self.pk}) 