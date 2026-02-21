from django.urls import path
from .views import (
    ExerciseListView, ExerciseDetailView,
    ExerciseCreateView, ExerciseUpdateView, ExerciseDeleteView
)

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise-list'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('create/', ExerciseCreateView.as_view(), name='exercise-create'),
    path('<int:pk>/update/', ExerciseUpdateView.as_view(), name='exercise-update'),
    path('<int:pk>/delete/', ExerciseDeleteView.as_view(), name='exercise-delete'),
]
