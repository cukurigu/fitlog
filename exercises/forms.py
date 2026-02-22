from django import forms
from .models import Exercise


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "muscle", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }