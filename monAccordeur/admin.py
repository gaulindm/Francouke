from django.contrib import admin
from .models import Instrument, Chord

# Inline editing for Chords in Instrument admin
class ChordInline(admin.TabularInline):
    model = Chord
    extra = 1  # Show 1 empty form for adding new Chords

# Custom admin for Instrument
@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'tuning')  # Show these fields in list view
    search_fields = ('name',)         # Enable search by instrument name
    inlines = [ChordInline]           # Add Chords inline for Instrument

# Custom admin for Chord
@admin.register(Chord)
class ChordAdmin(admin.ModelAdmin):
    list_display = ('name', 'instrument', 'frets','fingers')  # Show chord info
    list_filter = ('instrument',)                   # Filter by instrument
    search_fields = ('name', 'instrument__name')    # Search by chord or instrument name
