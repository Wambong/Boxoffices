# forms.py

from django import forms
from .models import Movie

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'  # Use all fields from the Movie model
