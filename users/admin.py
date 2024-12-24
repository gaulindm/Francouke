from django.contrib import admin
from .models import Profile
from .models import UserPreferences

admin.site.register(Profile)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'font_size', 'line_spacing', 'text_color', 'instrument', 'is_lefty')
    search_fields = ('user__username', 'user__email')
    list_filter = ('font_size', 'instrument', 'is_lefty')