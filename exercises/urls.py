from django.urls import path
from . import views

urlpatterns = [
    path("", views.exercise_list, name="exercise-list"),
    path("create/", views.exercise_create, name="exercise-create"),
    path("<int:pk>/delete/", views.exercise_delete, name="exercise-delete"),
]