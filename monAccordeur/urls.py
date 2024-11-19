# urls.py
from django.urls import path
from . import views

app_name = 'monAccordeur'  # Namespacing the app

urlpatterns = [
    
    path('draw-chords/', views.draw_chords, name='draw_chords'), 
      # Keeps specific name for chords route
    #path('chords/', views.get_chords_definition, name='chord_definitions'),  # Chord data (JSON)
]
