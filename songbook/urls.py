from django.urls import path
from .views import (
    SongListView, 
    SongCreateView,
    SongUpdateView,
    SongDeleteView,
    UserSongListView,
    transpose_song_view,
    ScoreView
)
from . import views

urlpatterns = [
    path('', SongListView.as_view(), name='songbook-home'),
    path('user/<str:username>', UserSongListView.as_view(), name='user-songs'),
    path('score/<int:pk>/', ScoreView.as_view(),name='score'),
    path('song/new/', SongCreateView.as_view(), name='song-create'),
    path('song/<int:pk>/update/', SongUpdateView.as_view(), name='song-update'),
    path('song/<int:pk>/delete/', SongDeleteView.as_view(), name='song-delete'),
    path('about/', views.about, name='songbook-about'),
    path('transpose/<int:song_id>/<str:new_key>/', transpose_song_view, name='transpose_song'),

]