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

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserPreference

@login_required
def update_preferences(request):
    if request.method == "POST":
        preferences = get_object_or_404(UserPreference, user=request.user)

        # ✅ Update Global Font Size
        preferences.font_size = request.POST.get("font_size", preferences.font_size)
        preferences.save()

        return JsonResponse({"status": "success", "font_size": preferences.font_size})

    return JsonResponse({"status": "error", "message": "Invalid request"})
