from rest_framework import generics

from .models import Course
from .serializers import CourseDetailSerializer, CourseListSerializer


class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.select_related('study_area').all()
    serializer_class = CourseListSerializer


class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.select_related('study_area').prefetch_related(
        'modules__lessons'
    )
    serializer_class = CourseDetailSerializer
    lookup_field = 'slug'
