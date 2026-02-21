from django.contrib import admin
from .models import Workout, WorkoutExercise, WorkoutSet


class WorkoutSetInline(admin.TabularInline):
    model = WorkoutSet
    extra = 1


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1
    show_change_link = True


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "duration_minutes")
    inlines = [WorkoutExerciseInline]


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    inlines = [WorkoutSetInline]

