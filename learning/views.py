from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Course, Lesson, Module, StudyArea
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    StudyAreaSerializer,
)


class StudyAreaViewSet(ModelViewSet):
    queryset = StudyArea.objects.all()
    serializer_class = StudyAreaSerializer


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ModuleViewSet(ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Module.objects.filter(course__owner=self.request.user)

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.owner != self.request.user:
            raise PermissionDenied('You cannot add modules to this course.')
        serializer.save()


class LessonViewSet(ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.filter(module__course__owner=self.request.user)

    def perform_create(self, serializer):
        module = serializer.validated_data['module']
        if module.course.owner != self.request.user:
            raise PermissionDenied('You cannot add lessons to this module.')
        serializer.save()
