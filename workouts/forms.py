from django import forms
from django.forms import inlineformset_factory
from datetime import date

from .models import Workout, WorkoutExercise, WorkoutSet


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["title", "date", "duration_minutes", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_date(self):
        workout_date = self.cleaned_data.get("date")
        if workout_date and workout_date > date.today():
            raise forms.ValidationError("Workout date cannot be in the future.")
        return workout_date


WorkoutSetFormSet = inlineformset_factory(
    parent_model=WorkoutExercise,
    model=WorkoutSet,
    fields=["set_number", "weight", "reps"],
    extra=0,
    can_delete=True,
)