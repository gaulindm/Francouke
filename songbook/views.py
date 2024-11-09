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
from django.db. models import Prefetch
from .parsers import parse_song_data
from .transposer import extract_chords
from unidecode import unidecode


#def score_view(request, song_id):
#    song = get_object_or_404(Song, id=song_id)  # Fetch the song based on the id
#    return render(request, 'score.html', {'score': song})  



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
    paginate_by = 15

    def get_queryset(self):
        # Sort by title and return
        return Song.objects.all()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_data = []

        for song in context['songs']:
            parsed_data = song.lyrics_with_chords  # Assuming this is already parsed and stored
            chords = extract_chords(parsed_data,unique=True)
            song_data.append({
                'song': song,
                'chords': ', '.join(chords)  # Join chords into a string for display
            })

        context['song_data'] = song_data
        return context


    
class UserSongListView (ListView):
    model = Song
    template_name = 'songbook/user_songs.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 15

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Song.objects.filter(contributor=user).order_by('songTitle')

class SongDetailView (DetailView):
    model = Song

class ScoreView(DetailView):
    model = Song
    template_name = 'songbook/song_simplescore.html' #While I am experimenting with scoreview
    context_object_name = 'score'

    def song_detail(request, song_id):
        song = get_object_or_404(Song, id=song_id)
        context = {
            'score': song,  # 'score' will map to the 'song' instance
        }
        return render(request, 'song_score.html', context)


class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = ['songTitle','songChordPro','metadata']
    def form_valid(self, form):
        form.instance.contributor = self.request.user
        return super().form_valid(form)

class SongUpdateView (LoginRequiredMixin, UpdateView):
    model = Song
    fields = ['songTitle', 'songChordPro','lyrics_with_chords','metadata']

    def form_valid(self, form):
        # Set the contributor to the current user
        form.instance.contributor = self.request.user
        
        # Parse the songChordPro field
        raw_lyrics = form.cleaned_data['songChordPro']
        parsed_lyrics = parse_song_data(raw_lyrics)
        
        # Update the lyrics_with_chords field with the parsed data
        form.instance.lyrics_with_chords = parsed_lyrics
        
        return super().form_valid(form)
        
    def test_func(self):
        song = self.get_object()
        return self.request.user == song.contributor





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