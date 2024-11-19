from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Chord
from .svg_generator import generate_chord_svg
from django.core.exceptions import ObjectDoesNotExist
import logging


def home(request):
    return HttpResponse("Welcome to Mon Accordeur!")

def about(request):
    return render(request,'monAccordeur/about.html')

def draw_chords(request):
    """
    Fetch specific chords for a given instrument, support left-handed players, 
    generate SVGs, and return the response.

    Query Parameters:
        instrument (str): The instrument name to filter by (e.g., "guitar", "ukulele").
        chords (str): Comma-separated list of desired chord names (e.g., "C,F,G").
        isLefty (bool): Whether to flip the chord diagram for left-handed players.
    """
    instrument = request.GET.get('instrument', 'ukulele').lower()
    chords_param = request.GET.get('chords', '')  # Get desired chords from query parameters
    desired_chords = chords_param.split(',') if chords_param else []
    is_lefty = request.GET.get('isLefty', 'false').lower() == 'true'  # Convert to boolean

    # Fetch chords for the specified instrument and desired names
    chords_queryset = Chord.objects.filter(
        instrument__name=instrument,
        name__in=desired_chords
    ) if desired_chords else Chord.objects.filter(instrument__name=instrument)

    found_chords = [chord.name for chord in chords_queryset]
    missing_chords = set(desired_chords) - set(found_chords)

    if missing_chords:
        error_message = (
            f"The following chords were not found for {instrument}: "
            f"{', '.join(missing_chords)}"
        )
        context = {
            'chords': chords_queryset,  # Show the found chords
            'instrument': instrument,
            'isLefty': is_lefty,
            'error': error_message
        }
        return render(request, 'monAccordeur/draw_chords.html', context)

    # Convert queryset to a list of dictionaries with SVGs
    chords = []
    for chord in chords_queryset:
        # Reverse frets and fingers if isLefty
        frets = chord.frets[::-1] if is_lefty else chord.frets
        fingers = chord.fingers[::-1] if is_lefty and chord.fingers else chord.fingers

        # Generate SVG
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

    context = {'chords': chords, 'instrument': instrument, 'isLefty': is_lefty}
    return render(request, 'monAccordeur/draw_chords.html', context)
