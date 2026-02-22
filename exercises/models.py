from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    muscle = models.ForeignKey("muscles.Muscle", on_delete=models.CASCADE, related_name="muscle")
    description = models.TextField(blank=True)
    is_custom = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="custom_exercises")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["muscle__name", "name"]