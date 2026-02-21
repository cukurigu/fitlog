from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView
from django.forms import inlineformset_factory
from django import forms as django_forms

from .models import Workout, WorkoutSet, WorkoutExercise
from .forms import WorkoutForm, WorkoutSetFormSet


class WorkoutListView(ListView):
    model = Workout
    template_name = "workouts/workout_list.html"
    context_object_name = "workouts"
    ordering = ["-date"]


class WorkoutDetailView(View):
    def get(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)

        merged = {}
        for we in workout.exercises.select_related("exercise").prefetch_related("sets"):
            exercise = we.exercise
            if exercise.id not in merged:
                merged[exercise.id] = {"exercise": exercise, "sets": []}
            merged[exercise.id]["sets"].extend(list(we.sets.all()))

        for entry in merged.values():
            for i, s in enumerate(entry["sets"], start=1):
                s.set_number = i

        return render(request, "workouts/workout_detail.html", {
            "workout": workout,
            "exercise_groups": list(merged.values()),
        })


def _build_set_formsets(post_data, exercise_formset):
    set_formsets = []
    for i, ex_form in enumerate(exercise_formset.forms):
        instance = ex_form.instance
        queryset = instance.sets.all() if instance.pk else WorkoutSet.objects.none()
        kwargs = dict(prefix=f"sets-{i}", instance=instance, queryset=queryset)
        if post_data is not None:
            set_formsets.append(WorkoutSetFormSet(post_data, **kwargs))
        else:
            set_formsets.append(WorkoutSetFormSet(**kwargs))
    return set_formsets


def _save_exercises_and_sets(workout, exercise_formset, set_formsets):
    for ex_form in exercise_formset.deleted_forms:
        if ex_form.instance.pk:
            ex_form.instance.delete()

    for i, ex_form in enumerate(exercise_formset.forms):
        if ex_form in exercise_formset.deleted_forms:
            continue
        if not ex_form.has_changed() and not ex_form.instance.pk:
            continue

        ex_instance = ex_form.save(commit=False)
        ex_instance.workout = workout
        if not ex_instance.order:
            ex_instance.order = i + 1
        ex_instance.save()

        set_formset = set_formsets[i]

        for set_form in set_formset.deleted_forms:
            if set_form.instance.pk:
                set_form.instance.delete()

        for set_num, set_form in enumerate(set_formset.forms, start=1):
            if set_form in set_formset.deleted_forms:
                continue
            if not set_form.has_changed() and not set_form.instance.pk:
                continue
            s = set_form.save(commit=False)
            s.workout_exercise = ex_instance
            if not s.set_number:
                s.set_number = set_num
            s.save()


def _make_exercise_formset(extra):
    return inlineformset_factory(
        Workout, WorkoutExercise,
        fields=["exercise", "order"],
        widgets={"order": django_forms.HiddenInput()},
        extra=extra,
        can_delete=True,
    )


class WorkoutCreateView(View):
    template_name = "workouts/workout_form.html"

    def _context(self, workout_form, exercise_formset, set_formsets):
        return {
            "form": workout_form,
            "exercise_formset": exercise_formset,
            "exercise_set_pairs": list(zip(exercise_formset.forms, set_formsets)),
            "mode": "create",
        }

    def get(self, request):
        workout_form = WorkoutForm()
        exercise_formset = _make_exercise_formset(extra=1)(prefix="exercises")
        set_formsets = _build_set_formsets(None, exercise_formset)
        return render(request, self.template_name,
                      self._context(workout_form, exercise_formset, set_formsets))

    def post(self, request):
        workout_form = WorkoutForm(request.POST)
        exercise_formset = _make_exercise_formset(extra=0)(request.POST, prefix="exercises")
        set_formsets = _build_set_formsets(request.POST, exercise_formset)

        forms_valid = (
            workout_form.is_valid()
            and exercise_formset.is_valid()
            and all(sf.is_valid() for sf in set_formsets)
        )

        if forms_valid:
            workout = workout_form.save()
            exercise_formset.instance = workout
            _save_exercises_and_sets(workout, exercise_formset, set_formsets)
            return redirect(workout.get_absolute_url())

        return render(request, self.template_name,
                      self._context(workout_form, exercise_formset, set_formsets))


class WorkoutUpdateView(View):
    template_name = "workouts/workout_form.html"

    def _context(self, workout, workout_form, exercise_formset, set_formsets):
        return {
            "workout": workout,
            "form": workout_form,
            "exercise_formset": exercise_formset,
            "exercise_set_pairs": list(zip(exercise_formset.forms, set_formsets)),
            "mode": "edit",
        }

    def get(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        workout_form = WorkoutForm(instance=workout)
        exercise_formset = _make_exercise_formset(extra=0)(instance=workout, prefix="exercises")
        set_formsets = _build_set_formsets(None, exercise_formset)
        return render(request, self.template_name,
                      self._context(workout, workout_form, exercise_formset, set_formsets))

    def post(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        workout_form = WorkoutForm(request.POST, instance=workout)
        exercise_formset = _make_exercise_formset(extra=0)(request.POST, instance=workout, prefix="exercises")
        set_formsets = _build_set_formsets(request.POST, exercise_formset)

        forms_valid = (
            workout_form.is_valid()
            and exercise_formset.is_valid()
            and all(sf.is_valid() for sf in set_formsets)
        )

        if forms_valid:
            workout = workout_form.save()
            _save_exercises_and_sets(workout, exercise_formset, set_formsets)
            return redirect(workout.get_absolute_url())

        return render(request, self.template_name,
                      self._context(workout, workout_form, exercise_formset, set_formsets))


class WorkoutDeleteView(DeleteView):
    model = Workout
    template_name = "workouts/workout_confirm_delete.html"
    success_url = reverse_lazy("workout-list")