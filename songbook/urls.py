from django.urls import path
from .views import (
    SongListView, 
    SongDetailView,
    SongCreateView,
    SongUpdateView,
    SongDeleteView,
    UserSongListView,
    ScoreView
)
from . import views

urlpatterns = [
    path('', SongListView.as_view(), name='songbook-home'),
    path('user/<str:username>', UserSongListView.as_view(), name='user-songs'),
    path('song/<int:pk>/', SongDetailView.as_view(), name='song-detail'),
    path('score/<int:pk>/', ScoreView.as_view(),name='score'),
    path('song/new/', SongCreateView.as_view(), name='song-create'),
    path('song/<int:pk>/update/', SongUpdateView.as_view(), name='song-update'),
    path('song/<int:pk>/delete/', SongDeleteView.as_view(), name='song-delete'),
    path('about/', views.about, name='songbook-about'),

]