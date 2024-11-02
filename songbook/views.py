from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView, 
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    )
from .models import Song
from unidecode import unidecode







def home(request):
    context = {
        'songs':Song.objects.all()
    }
    return render(request, 'songbook/home.html',context)

class SongListView (ListView):
    model = Song
    template_name = 'songbook/home.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 5

    def get_queryset(self):
        # Retrieve all songs and sort them by an unaccented title
        songs = Song.objects.all()
        # Sort using unidecode to remove accents for sorting purposes
        return sorted(songs, key=lambda song: unidecode(song.songTitle or ""))
    
class UserSongListView (ListView):
    model = Song
    template_name = 'songbook/user_songs.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Song.objects.filter(contributor=user).order_by('songTitle')

class SongDetailView (DetailView):
    model = Song

class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = ['songTitle','songChordPro','metadata']
    def form_valid(self, form):
        form.instance.contributor = self.request.user
        return super().form_valid(form)

class SongUpdateView (LoginRequiredMixin, UpdateView):
    model = Song
    fields = ['songTitle', 'songChordPro','metadata']

    def form_valid(self, form):
        form.instance.contributor = self.request.user
        return super().form_valid(form)
        
    def test_func(self):
        song= self.get_object()
        if self.request.user ==song.contributor:
            return True
        return False





class SongDeleteView (LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Song
    success_url = '/'

    def test_func(self):
        song = self.get_object()
        if self.request.user == song.contributor:
            return True
        return False 


def about(request):
    return render (request, 'songbook/about.html',{'title':about})