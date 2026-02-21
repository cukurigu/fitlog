from django.contrib import admin
from .models import Muscle

@admin.register(Muscle)
class MuscleAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
    list_filter = ["category",]
    search_fields = ["name",]
