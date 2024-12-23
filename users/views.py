from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from .forms import UserRegisterForm
from django.http import JsonResponse
from .models import UserPreferences


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created!  You are now able to log in!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html',{'form':form})


#@login_required
#def profile(request):
#    return render(request, 'users/profile.html')


@login_required
def update_preferences(request):
    if request.method == "POST":
        preferences = get_object_or_404(UserPreferences, user=request.user)
        preferences.font_size = request.POST.get("font_size", preferences.font_size)
        preferences.line_spacing = request.POST.get("line_spacing", preferences.line_spacing)
        preferences.text_color = request.POST.get("text_color", preferences.text_color)
        preferences.chord_color = request.POST.get("chord_color", preferences.chord_color)
        preferences.instrument = request.POST.get("instrument", preferences.instrument)
        preferences.is_lefty = request.POST.get("is_lefty") == "true"
        preferences.chord_diagram_position = request.POST.get(
            "chord_diagram_position", preferences.chord_diagram_position
        )
        preferences.chord_placement = request.POST.get("chord_placement", preferences.chord_placement)
        preferences.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"})
