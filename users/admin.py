from django.contrib import admin
from .models import Profile
from .models import UserPreference

admin.site.register(Profile)




@admin.register(UserPreference)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'instrument', 'is_lefty','is_printing_alternate_chord')
    list_editable = ('is_lefty', 'is_printing_alternate_chord')
    search_fields = ('user__username', 'user__email')
    list_filter = ('font_size', 'instrument', 'is_lefty')