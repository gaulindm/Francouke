from django.contrib import admin
from .models import Song


@admin.register(Song)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ['songTitle', 'get_artist', 'get_tags']
    search_fields = ['songTitle', 'metadata']

    def get_artist(self, obj):
        # Extract the artist from the metadata JSON field
        return obj.metadata.get('artist', 'Unknown') if obj.metadata else 'No Metadata'
    get_artist.short_description = 'Artist'  # Column title in the admin

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def get_tags(self, obj):
        return ", ".join(o for o in obj.tags.names())