from django.contrib import admin
from .models import Song


@admin.register(Song)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ['songTitle', 'metadata']
    search_fields = ['songTitle', 'metadata']