from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView
from django.forms import inlineformset_factory
from django import forms as django_forms
from django.db.models import Max
import json
from datetime import date, timedelta
import collections

from .models import Workout, WorkoutSet, WorkoutExercise
from .forms import WorkoutForm, WorkoutSetFormSet


def _get_default_user():
    from django.contrib.auth.models import User
    return User.objects.first()


def _make_exercise_formset(extra):
    return inlineformset_factory(
        Workout, WorkoutExercise,
        fields=["exercise", "order"],
        widgets={"order": django_forms.HiddenInput()},
        extra=extra,
        can_delete=True,
    )


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


def _get_personal_records(user):
    records = {}
    sets = WorkoutSet.objects.filter(
        workout_exercise__workout__user=user
    ).select_related("workout_exercise__exercise")
    for s in sets:
        ex_id = s.workout_exercise.exercise_id
        if ex_id not in records or s.weight > records[ex_id]:
            records[ex_id] = s.weight
    return records


def _contribution_data(user):
    today = date.today()
    one_year_ago = today - timedelta(days=364)

    workout_dates = set(
        Workout.objects.filter(user=user, date__gte=one_year_ago)
        .values_list("date", flat=True)
    )

    start = one_year_ago - timedelta(days=one_year_ago.weekday() + 1)
    if start.weekday() != 6:
        start = start - timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    current = start
    while current <= today:
        week = []
        for d in range(7):
            day = current + timedelta(days=d)
            count = 1 if day in workout_dates else 0
            if day > today:
                level = -1
            elif count:
                level = 2
            else:
                level = 0
            week.append({"date": day.isoformat(), "count": count, "level": level})
        weeks.append(week)
        current += timedelta(weeks=1)

    streak = 0
    rest_days = 0
    check = today
    while True:
        if check in workout_dates:
            streak += 1
            rest_days = 0
        else:
            rest_days += 1
            if rest_days > 2:
                break
        check -= timedelta(days=1)
        if check < one_year_ago:
            break

    return weeks, streak, workout_dates


class WorkoutListView(ListView):
    model = Workout
    template_name = "workouts/workout_list.html"
    context_object_name = "workouts"
    ordering = ["-date"]

    def get_queryset(self):
        user = _get_default_user()
        return Workout.objects.filter(user=user).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = _get_default_user()
        weeks, streak, _ = _contribution_data(user)
        context["contribution_weeks"] = json.dumps(weeks)
        context["streak"] = streak
        return context


class WorkoutDetailView(View):
    def get(self, request, pk):
        user = _get_default_user()
        workout = get_object_or_404(Workout, pk=pk, user=user)
        all_records = _get_personal_records(user)

        merged = {}
        for we in workout.exercises.select_related("exercise").prefetch_related("sets"):
            exercise = we.exercise
            if exercise.id not in merged:
                merged[exercise.id] = {"exercise": exercise, "sets": [], "has_pr": False}
            merged[exercise.id]["sets"].extend(list(we.sets.all()))

        for entry in merged.values():
            for i, s in enumerate(entry["sets"], start=1):
                s.set_number = i
            ex_id = entry["exercise"].id
            best_in_workout = max((s.weight for s in entry["sets"]), default=None)
            if best_in_workout and all_records.get(ex_id) == best_in_workout:
                entry["has_pr"] = True

        return render(request, "workouts/workout_detail.html", {
            "workout": workout,
            "exercise_groups": list(merged.values()),
        })


def exercise_progress(request, exercise_id):
    from exercises.models import Exercise
    user = _get_default_user()
    exercise = get_object_or_404(Exercise, pk=exercise_id)

    rows = (
        WorkoutSet.objects
        .filter(
            workout_exercise__exercise=exercise,
            workout_exercise__workout__user=user,
        )
        .select_related("workout_exercise__workout")
        .order_by("workout_exercise__workout__date")
    )

    best_by_date = collections.OrderedDict()
    for s in rows:
        d = s.workout_exercise.workout.date.isoformat()
        if d not in best_by_date or s.weight > best_by_date[d]:
            best_by_date[d] = float(s.weight)

    chart_data = {
        "labels": list(best_by_date.keys()),
        "data": list(best_by_date.values()),
    }

    return render(request, "workouts/exercise_progress.html", {
        "exercise": exercise,
        "chart_data": json.dumps(chart_data),
    })


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
            workout = workout_form.save(commit=False)
            workout.user = _get_default_user()
            workout.save()
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
        user = _get_default_user()
        workout = get_object_or_404(Workout, pk=pk, user=user)
        workout_form = WorkoutForm(instance=workout)
        exercise_formset = _make_exercise_formset(extra=0)(instance=workout, prefix="exercises")
        set_formsets = _build_set_formsets(None, exercise_formset)
        return render(request, self.template_name,
                      self._context(workout, workout_form, exercise_formset, set_formsets))

    def post(self, request, pk):
        user = _get_default_user()
        workout = get_object_or_404(Workout, pk=pk, user=user)
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

    def get_queryset(self):
        user = _get_default_user()
        return Workout.objects.filter(user=user)