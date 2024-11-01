Installation tricks read me

This files contains fixes to errors in the video.  Most likely du to different version.


I have opted to disable profiles... I don't want to show profile pics in the future SongListView
When needed.  Remove comments in base.html

I have chosen to ignore Part 9 for the moment.  There is no need to update profile pic

Issues with forms|crispy

Solution from Youtube comments:
If anyone is doing this tutorial and having troubles with crispy forms, with the help of tutorial and some comments, I found that this works:

1) pip install django_crispy_forms
2) pip install crispy_bootstrap4
3) Add both of these to INSTALLED_APPS:
    'crispy_forms',
    'crispy_bootstrap4',
4) Add both of these at the bottom:
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"

CRISPY_TEMPLATE_PACK = 'bootstrap4'
5) Use {% load crispy_forms_tags %} and {{ form|crispy }} in the html file.