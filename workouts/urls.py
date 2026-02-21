from django.urls import path
from .views import (
    WorkoutListView,
    WorkoutDetailView,
    WorkoutCreateView,
    WorkoutUpdateView,
    WorkoutDeleteView,
)

urlpatterns = [
    path("", WorkoutListView.as_view(), name="workout-list"),
    path("new/", WorkoutCreateView.as_view(), name="workout-create"),
    path('<int:pk>/', WorkoutDetailView.as_view(), name='workout-detail'),
    path("<int:pk>/edit/", WorkoutUpdateView.as_view(), name="workout-update"),
    path("<int:pk>/delete/", WorkoutDeleteView.as_view(), name="workout-delete"),
]
