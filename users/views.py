from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from .forms import UserRegisterForm
from django.http import JsonResponse
from .models import UserPreference


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
        # Fetch or create the user's preferences
        preferences = get_object_or_404(UserPreferences, user=request.user)
        
        # Update font size
        preferences.font_size = request.POST.get("font_size", preferences.font_size)
        
        # Update line spacing
        preferences.line_spacing = request.POST.get("line_spacing", preferences.line_spacing)
        
        # Update text color
        preferences.text_color = request.POST.get("text_color", preferences.text_color)
        
        # Update chord color
        preferences.chord_color = request.POST.get("chord_color", preferences.chord_color)
        
        # Update instrument
        valid_instruments = ["guitar", "ukulele", "baritone_ukulele", "banjo", "mandolin"]
        instrument = request.POST.get("instrument", preferences.instrument)
        if instrument in valid_instruments:
            preferences.instrument = instrument
        else:
            return JsonResponse({"status": "error", "message": "Invalid instrument selected"})
        
        # Update left-handed mode
        preferences.is_lefty = request.POST.get("is_lefty") == "true"
        
        # Update chord diagram position
        preferences.chord_diagram_position = request.POST.get(
            "chord_diagram_position", preferences.chord_diagram_position
        )
        
        # Update chord placement
        preferences.chord_placement = request.POST.get("chord_placement", preferences.chord_placement)
        
        # Save the updated preferences
        preferences.save()
        
        # Return a JSON response with the updated preferences
        return JsonResponse({
            "status": "success",
            "updated_preferences": {
                "font_size": preferences.font_size,
                "line_spacing": preferences.line_spacing,
                "text_color": preferences.text_color,
                "chord_color": preferences.chord_color,
                "instrument": preferences.instrument,
                "is_lefty": preferences.is_lefty,
                "chord_diagram_position": preferences.chord_diagram_position,
                "chord_placement": preferences.chord_placement,
            }
        })

    return JsonResponse({"status": "error", "message": "Invalid request"})
