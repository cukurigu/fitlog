from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Exercise
from .forms import ExerciseForm

# List all exercises
class ExerciseListView(ListView):
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'

# Exercise detail
class ExerciseDetailView(DetailView):
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'exercise'

# Create exercise
class ExerciseCreateView(CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'exercises/exercise_form.html'
    success_url = reverse_lazy('exercise-list')

# Update exercise
class ExerciseUpdateView(UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'exercises/exercise_form.html'
    success_url = reverse_lazy('exercise-list')

# Delete exercise
class ExerciseDeleteView(DeleteView):
    model = Exercise
    template_name = 'exercises/exercise_confirm_delete.html'
    success_url = reverse_lazy('exercise-list')

