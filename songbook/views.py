import os
import pdfkit
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
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
from django.views import View
from django.db. models import Prefetch
from .parsers import parse_song_data
from .transposer import extract_chords, calculate_steps, transpose_lyrics, detect_key
from unidecode import unidecode
from django.http import HttpResponse


def generate_pdf(request, song_id):
    song = get_object_or_404(Song, id=song_id)  # Ensure you fetch the song object
    context = {
        'score': song,
        'object': song,  # Add `object` to the context
    }
    html_content = render_to_string('songbook/song_simplescore.html', context)

    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')  # Update path as necessary
    pdf = pdfkit.from_string(html_content, False, configuration=config, options={
    'page-size': 'A4',
    'encoding': "UTF-8",
    'enable-local-file-access': True,
    'debug-javascript': True,
    'log-level': 'debug',  # Enable detailed logging
})

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="score.pdf"'
    return response

   


def home(request):
    context = {
        'songs':Song.objects.all()
    }
    return render(request, 'songbook/home.html',context)

class SongListView(ListView):
    model = Song
    template_name = 'songbook/song_list.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_data = []

        for song in context['songs']:
            parsed_data = song.lyrics_with_chords or ""
            chords = extract_chords(parsed_data, unique=True) if parsed_data else []
            song_data.append({
                'song': song,
                'chords': ', '.join(chords)
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


#This is second column of home.html
class ScoreView(DetailView):
    model = Song
    template_name = 'songbook/song_simplescore.html'  # Temporary template for experiments 
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

class SongUpdateView(LoginRequiredMixin, UpdateView):
    model = Song
    fields = ['songTitle', 'songChordPro', 'lyrics_with_chords', 'metadata']
    success_url = reverse_lazy('songbook-home')  # Redirect after success

    def form_valid(self, form):
        # Assign the contributor to the current user
        form.instance.contributor = self.request.user
        
        # Parse the songChordPro field
        raw_lyrics = form.cleaned_data['songChordPro']
        try:
            # Attempt to parse the songChordPro data
            parsed_lyrics = parse_song_data(raw_lyrics)
        except Exception as e:
            # Handle errors in parsing gracefully
            form.add_error('songChordPro', f"Error parsing song data: {e}")
            return self.form_invalid(form)
        
        # Update the lyrics_with_chords field with parsed data
        form.instance.lyrics_with_chords = parsed_lyrics
        return super().form_valid(form)

    def get_object(self, queryset=None):
        # Ensure only the contributor can update the song
        obj = super().get_object(queryset)
        if obj.contributor != self.request.user:
            raise PermissionDenied("You do not have permission to edit this song.")
        return obj




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