from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max
from .models import Exercise
from .forms import ExerciseForm
from muscles.models import Muscle


@login_required
def exercise_list(request):
    muscle_id = request.GET.get("muscle")
    exercises = Exercise.objects.select_related("muscle")
    muscles = Muscle.objects.all()

    if muscle_id:
        exercises = exercises.filter(muscle_id=muscle_id)

    grouped = {}
    for ex in exercises:
        muscle_name = ex.muscle.name
        if muscle_name not in grouped:
            grouped[muscle_name] = []
        grouped[muscle_name].append(ex)

    return render(request, "exercises/exercise_list.html", {
        "grouped": grouped,
        "muscles": muscles,
        "selected_muscle": int(muscle_id) if muscle_id else None,
    })


@login_required
def exercise_create(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.is_custom = True
            exercise.created_by = request.user
            exercise.save()
            messages.success(request, f'"{exercise.name}" added successfully.')
            return redirect("exercise-list")
    else:
        form = ExerciseForm()
    return render(request, "exercises/exercise_form.html", {"form": form})


@login_required
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk, is_custom=True, created_by=request.user)
    if request.method == "POST":
        name = exercise.name
        exercise.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect("exercise-list")
    return render(request, "exercises/exercise_confirm_delete.html", {"exercise": exercise})