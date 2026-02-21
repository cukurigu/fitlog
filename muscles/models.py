from django.db import models

class Muscle(models.Model):
    CATEGORY_CHOICES = [
        ("Push", "Pushing"),
        ("Pull", "Pulling"),
        ("Legs", "Legs"),
        ("Core", "Core"),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name
