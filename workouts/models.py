from django.db import models
from django.urls import reverse

class Workout(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.date})"

    def get_absolute_url(self):
        return reverse('workout-detail', args=[str(self.id)])

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey('exercises.Exercise', on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.exercise.name} in {self.workout.title}"

class WorkoutSet(models.Model):
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE, related_name="sets")
    set_number = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    reps = models.PositiveIntegerField()

    class Meta:
        ordering = ["set_number"]

    def __str__(self):
        return f"Set {self.set_number}: {self.weight}kg x {self.reps}"
