# forms.py
from django import forms
from taggit.models import Tag

class TagFilterForm(forms.Form):
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        label='Select Tag',
        required=True
    )
