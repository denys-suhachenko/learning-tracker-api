from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Lesson, Module, StudyArea
from .serializers import (
    CourseDetailSerializer,
    CourseSerializer,
    LessonNestedSerializer,
    LessonSerializer,
    ModuleDetailSerializer,
    ModuleSerializer,
    StudyAreaSerializer,
)


class StudyAreaViewSet(viewsets.ModelViewSet):
    queryset = StudyArea.objects.all()
    serializer_class = StudyAreaSerializer


class CourseViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if self.action == 'retrieve':
            return Course.objects.select_related('study_area').prefetch_related(
                'modules__lessons'
            )
        return Course.objects.select_related('study_area').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = (
        Module.objects.select_related('course')
        .prefetch_related('lessons')
        .order_by('course_id', 'order', 'id')
    )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModuleDetailSerializer
        return ModuleSerializer

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        module = self.get_object()
        serializer = LessonNestedSerializer(module.lessons.all(), many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('module', 'module__course').order_by(
        'module_id', 'order', 'id'
    )
    serializer_class = LessonSerializer
