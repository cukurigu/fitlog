from django.contrib import admin
from .models import Exercise

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["name", "muscle"]
    list_filter = ["muscle__category",]
    search_fields = ["name",]
