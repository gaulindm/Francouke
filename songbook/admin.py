from django.contrib import admin
from .models import Song


@admin.register(Song)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ['songTitle', 'get_artist', 'get_year',  'get_youtube', 'get_tags']
    search_fields = ['songTitle', 'metadata__artist', 'get_artist','abc_notation']
    
    
    ordering = ('metadata__artist',)

    def get_year(self, obj):
        # Extract the artist from the metadata JSON field
        return obj.metadata.get('year', 'Unknown') if obj.metadata else 'No Metadata'
    get_year.admin_order_field = 'metadata__year'
    get_year.short_description = 'Year'  # Column title in the admin

    def get_youtube(self, obj):
        # Extract the artist from the metadata JSON field
        return obj.metadata.get('youtube', '') if obj.metadata else 'No Metadata'
    get_year.admin_order_field = 'metadata__youtube'
    get_year.short_description = 'youtube'  # Column title in the admin




    def get_artist(self, obj):
        # Extract the artist from the metadata JSON field
        return obj.metadata.get('artist', 'Unknown') if obj.metadata else 'No Metadata'
    get_artist.admin_order_field = 'metadata__artist'
    get_artist.short_description = 'Artist'  # Column title in the admin

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def get_tags(self, obj):
        return ", ".join(o for o in obj.tags.names())