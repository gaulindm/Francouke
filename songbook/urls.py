from django.urls import path
from songbook import views
from .views import (
    SongListView, 
    SongCreateView,
    SongUpdateView,
    SongDeleteView,
    UserSongListView,
    ScoreView
)
from . import views
from .views import generate_audio_from_abc

urlpatterns = [
    path('', SongListView.as_view(), name='songbook-home'),
    path('user/<str:username>', UserSongListView.as_view(), name='user-songs'),
    path('score/<int:pk>/', ScoreView.as_view(),name='score'),
    path('song/new/', SongCreateView.as_view(), name='song-create'),
    path('song/<int:pk>/update/', SongUpdateView.as_view(), name='song-update'),
    path('song/<int:pk>/delete/', SongDeleteView.as_view(), name='song-delete'),
    path('about/', views.about, name='songbook-about'),
    path('', SongListView.as_view(), name='song_list'),  # Define a name for this pattern
    path('generate-styled-song-pdf/', views.generate_styled_song_pdf, name='generate_styled_song_pdf'),
    path('generate-song-pdf/<int:song_id>/', views.generate_single_song_pdf, name='generate_single_song_pdf'),
    path('song/<int:song_id>/generate-audio/', generate_audio_from_abc, name='generate_audio_from_abc'),

]
