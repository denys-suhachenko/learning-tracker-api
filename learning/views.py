from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Course, Lesson, Module, StudyArea
from .serializers import (
    CourseDetailReadSerializer,
    CourseDetailSerializer,
    CourseReadSerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    StudyAreaSerializer,
)


class StudyAreaViewSet(ModelViewSet):
    serializer_class = StudyAreaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudyArea.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    list=extend_schema(responses=CourseReadSerializer(many=True)),
    retrieve=extend_schema(responses=CourseDetailReadSerializer),
    create=extend_schema(responses=CourseReadSerializer),
    update=extend_schema(responses=CourseReadSerializer),
    partial_update=extend_schema(responses=CourseReadSerializer),
)
class CourseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Course.objects.filter(owner=self.request.user)
            .select_related('study_area')
            .prefetch_related('modules', 'modules__lessons')
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

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

    def perform_update(self, serializer):
        if serializer.instance.module.course.owner != self.request.user:
            raise PermissionDenied('You cannot update this lesson.')
        serializer.save()
