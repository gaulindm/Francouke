# chord_filters.py
import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def format_chords(text):
    # Step 1: Remove metadata tags like [title:], [artist:], etc.
    #text = re.sub(r'\[(title|artist|key|capo|time|tempo):[^\]]*\]', '', text, flags=re.IGNORECASE)
    
    # Step 2: Format chords in brackets with bold styling
    text = re.sub(r'\[([A-G][#b]?m?(sus|add|dim|maj|min)?\d?)\]', r'<span class="chord">[\1]</span>', text)
    
    # Step 3: Preserve line breaks by replacing \n with <br> tags
    text = text.replace('\n', '<br>')

    return mark_safe(text)
    