from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from django.contrib.auth.models import User
from monAccordeur.models import Chord
from monAccordeur.svg_generator import generate_chord_svg
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
from .transposer import extract_chords, calculate_steps, transpose_lyrics, detect_key
from unidecode import unidecode



#def score_view(request, song_id):
#    song = get_object_or_404(Song, id=song_id)  # Fetch the song based on the id
#    return render(request, 'score.html', {'score': song})  

def song_with_chords_view(request, song_id, new_key, instrument='ukulele'):
    # Data for the left side (transposed song)
    song = get_object_or_404(Song, id=song_id)
    parsed_data = song.lyrics_with_chords  # Assuming this is parsed and stored
    original_key = song.metadata.get('key') or detect_key(parsed_data)
    steps = calculate_steps(original_key, new_key)
    transposed_lyrics = transpose_lyrics(parsed_data, steps)

    # Data for the right side (chord diagrams)
    chords_param = request.GET.get('chords', '')  # Optional: Pass chords via query params
    desired_chords = chords_param.split(',') if chords_param else []
    is_lefty = request.GET.get('isLefty', 'false').lower() == 'true'

    # Fetch chords for the instrument
    chords_queryset = Chord.objects.filter(
        instrument__name=instrument,
        name__in=desired_chords
    ) if desired_chords else Chord.objects.filter(instrument__name=instrument)

    chords = []
    for chord in chords_queryset:
        frets = chord.frets[::-1] if is_lefty else chord.frets
        fingers = chord.fingers[::-1] if is_lefty and chord.fingers else chord.fingers
        chords.append({
            "name": chord.name,
            "frets": frets,
            "fingers": fingers,
            "svg": generate_chord_svg(
                chord_name=chord.name,
                frets=frets,
                fingers=fingers
            )
        })

    context = {
        'score': song,
        'transposed_lyrics': transposed_lyrics,
        'chords': chords,
        'instrument': instrument,
        'isLefty': is_lefty,
    }
    return render(request, 'songbook/song_with_chords.html', context)






def transpose_song_view(request, song_id, new_key):
    song = get_object_or_404(Song, id=song_id)
    parsed_data = song.lyrics_with_chords  # Assuming this is already parsed and stored
    original_key = song.metadata.get('key') or detect_key(parsed_data)
    steps = calculate_steps(original_key, new_key)
    transposed_lyrics = transpose_lyrics(parsed_data, steps)
    return render(request, 'songbook/song_simplescore.html', {'score': song, 'transposed_lyrics': transposed_lyrics})

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

#This is the view that works well in first column of home.html
class ScoreView(DetailView):
    model = Song
    template_name = 'songbook/song_simplescore.html' 
    context_object_name = 'score'

#This is second column of home.html
class NewScoreView(DetailView):
    model = Song
    template_name = 'songbook/new_score_view.html'  # Temporary template for experiments 
    context_object_name = 'score'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add custom context data for experimentation
        context['experiment'] = "This is a test for the new score view"
        return context    


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