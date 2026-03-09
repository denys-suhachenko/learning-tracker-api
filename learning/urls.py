from django.urls import path

from .views import CourseDetailAPIView, CourseListAPIView

urlpatterns = [
    path('courses/', CourseListAPIView.as_view(), name='course-list'),
    path('courses/<slug:slug>/', CourseDetailAPIView.as_view(), name='course-detail'),
]
