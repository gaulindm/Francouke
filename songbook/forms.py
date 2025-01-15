# forms.py
from django import forms
from taggit.models import Tag

class TagFilterForm(forms.Form):
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        label='Select Tag',
        required=True
    )

class SongForm(forms.Form):
    artist = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Artist Name", "class": "form-control"}),
        label="Artist"
    )
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Song Title", "class": "form-control"}),
        label="Title"
    )
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"placeholder": "Paste your song content here", "class": "form-control", "rows": 10}),
        label="Content"
    )