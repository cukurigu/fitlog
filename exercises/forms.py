from django import forms
from .models import Exercise

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "muscle", "description"]


    def clean_intensity(self):
        intensity = self.cleaned_data.get('intensity')
        if not 1 <= intensity <= 10:
            raise forms.ValidationError("Intensity must be between 1 and 10.")
        return intensity