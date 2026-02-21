from django.db import models
from muscles.models import Muscle


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    muscle = models.ForeignKey("muscles.Muscle", on_delete=models.CASCADE, related_name="muscle")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
