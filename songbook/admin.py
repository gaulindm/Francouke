from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Value
from django.db.models.functions import Concat
from .models import Song


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['songTitle', 'get_artist', 'get_year', 'get_youtube', 'get_tags']
    search_fields = ['songTitle', 'metadata__artist']
    ordering = ('metadata__artist',)

    def get_year(self, obj):
        return obj.metadata.get('year', 'Unknown') if obj.metadata else 'No Metadata'
    get_year.admin_order_field = 'metadata__year'
    get_year.short_description = 'Year'

    def get_youtube(self, obj):
        youtube_url = obj.metadata.get('youtube', '') if obj.metadata else ''
        return format_html('<a href="{}" target="_blank">{}</a>', youtube_url, youtube_url) if youtube_url else 'No Metadata'
    get_youtube.admin_order_field = 'metadata__youtube'
    get_youtube.short_description = 'YouTube'

    def get_artist(self, obj):
        return obj.metadata.get('artist', 'Unknown') if obj.metadata else ''
    get_artist.admin_order_field = 'metadata__artist'
    get_artist.short_description = 'Artist'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Annotate tags into a single string for sorting
        return queryset.annotate(
            tags_string=Concat('tags__name', Value(', '))  # Adjust for your field structure
        )

    def get_tags(self, obj):
        return ", ".join(o for o in obj.tags.names())
    get_tags.admin_order_field = 'tags_string'  # Enable sorting by annotated field
    get_tags.short_description = 'Tags'
