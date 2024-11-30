from django.urls import path
from .views import (
    SongListView, 
    SongCreateView,
    SongUpdateView,
    SongDeleteView,
    UserSongListView,
    transpose_song_view,
    NewScoreView,
    ChordDiagramsView,
    ScoreView
)
from . import views

urlpatterns = [
    path('', SongListView.as_view(), name='songbook-home'),
    path('user/<str:username>', UserSongListView.as_view(), name='user-songs'),
    path('score/<int:pk>/', ScoreView.as_view(),name='score'),
    path('song/new/', SongCreateView.as_view(), name='song-create'),
    path('chords/<str:chords>/', ChordDiagramsView.as_view(), name='chord-diagrams'),
    path('song/<int:pk>/update/', SongUpdateView.as_view(), name='song-update'),
    path('song/<int:pk>/delete/', SongDeleteView.as_view(), name='song-delete'),
    path('about/', views.about, name='songbook-about'),
    path('transpose/<int:song_id>/<str:new_key>/', transpose_song_view, name='transpose_song'),
    path('song/<int:song_id>/with-chords/<str:new_key>/', views.song_with_chords_view, name='song_with_chords'),
    path('newscore/<int:pk>/', NewScoreView.as_view(), name='newscore'),

]