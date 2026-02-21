from django.urls import path
from .views import (
    MuscleListView,
    MuscleCreateView,
    MuscleUpdateView,
    MuscleDeleteView,
)

urlpatterns = [
    path("", MuscleListView.as_view(), name="muscle-list"),
    path("new/", MuscleCreateView.as_view(), name="muscle-create"),
    path("<int:pk>/edit/", MuscleUpdateView.as_view(), name="muscle-update"),
    path("<int:pk>/delete/", MuscleDeleteView.as_view(), name="muscle-delete"),
]
