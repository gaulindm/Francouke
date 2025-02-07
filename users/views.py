from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserPreference
from django.urls import reverse
from .forms import UserPreferenceForm
from songbook.models import SongFormatting


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')

            messages.success(
                request,
                f'Compte créé pour {username} ! Visitez votre page <a href="{reverse("users:user_preferences")}">Préférences</a> pour personnaliser vos paramètres si vous prévoyez de générer des fichiers PDF avec des diagrammes d\'accords.'
            )

            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html',{'form':form})


@login_required
def user_preference_view(request):
    # Get or create the user's preferences
    preferences, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            return redirect('/')  # Replace with your desired redirect URL
    else:
        form = UserPreferenceForm(instance=preferences)

    return render(request, 'users/user_preference_form.html', {'form': form})

@login_required
def update_preferences(request):
    if request.method == "POST":
        try:
            print("🔹 Received update request:", request.POST)  # ✅ Debugging

            # Fetch User Preferences
            preferences = get_object_or_404(UserPreference, user=request.user)

            # Fetch or create the Song Formatting entry (Ensure each song has its own formatting)
            song_id = request.POST.get("song_id")  # Ensure this is sent from frontend
            song_formatting, created = SongFormatting.objects.get_or_create(song_id=song_id, user=request.user)

            # ✅ Update User Preferences (if needed)
            preferences.font_size = request.POST.get("font_size", preferences.font_size)
            preferences.line_spacing = request.POST.get("line_spacing", preferences.line_spacing)
            preferences.text_color = request.POST.get("text_color", preferences.text_color)
            preferences.chord_color = request.POST.get("chord_color", preferences.chord_color)
            preferences.instrument = request.POST.get("instrument", preferences.instrument)
            preferences.is_lefty = request.POST.get("is_lefty") == "true"
            preferences.chord_diagram_position = request.POST.get("chord_diagram_position", preferences.chord_diagram_position)
            preferences.save()

            # ✅ Update Song Formatting Preferences
            song_formatting.font_size = request.POST.get("font_size", song_formatting.font_size)
            song_formatting.line_spacing = request.POST.get("line_spacing", song_formatting.line_spacing)
            song_formatting.text_color = request.POST.get("text_color", song_formatting.text_color)
            song_formatting.chord_color = request.POST.get("chord_color", song_formatting.chord_color)
            song_formatting.chord_placement = request.POST.get("chord_placement", song_formatting.chord_placement)
            song_formatting.save()

            print("✅ Song formatting saved:", song_formatting.font_size, song_formatting.text_color)  # ✅ Debugging

            return JsonResponse({"status": "success", "updated_preferences": {
                "font_size": song_formatting.font_size,
                "line_spacing": song_formatting.line_spacing,
                "text_color": song_formatting.text_color,
                "chord_color": song_formatting.chord_color,
                "chord_placement": song_formatting.chord_placement,
            }})
        except Exception as e:
            print("❌ Error:", str(e))  # ✅ Debugging
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})