from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Muscle

class MuscleListView(ListView):
    model = Muscle
    template_name = "muscle/muscle_list.html"
    context_object_name = "muscles"


class MuscleCreateView(CreateView):
    model = Muscle
    fields = ["name", "category"]
    template_name = "muscle/muscle_form.html"
    success_url = reverse_lazy("muscle-list")


class MuscleUpdateView(UpdateView):
    model = Muscle
    fields = ["name", "category"]
    template_name = "muscle/muscle_form.html"
    success_url = reverse_lazy("muscle-list")


class MuscleDeleteView(DeleteView):
    model = Muscle
    template_name = "muscle/muscle_confirm_delete.html"
    success_url = reverse_lazy("muscle-list")
