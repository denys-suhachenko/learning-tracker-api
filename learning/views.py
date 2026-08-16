from django.db.models import Count, F, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Course, Lesson, Module, StudyArea
from .serializers import (
    ContinueLearningCourseSerializer,
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

    @action(
        detail=False,
        methods=['get'],
        url_path='continue-learning',
    )
    def continue_learning(self, request):
        courses = (
            Course.objects.filter(
                owner=request.user,
                status=Course.Status.ACTIVE,
            )
            .annotate(
                total_lessons=Count(
                    'modules__lessons',
                    distinct=True,
                ),
                completed_lessons=Count(
                    'modules__lessons',
                    filter=Q(modules__lessons__status=Lesson.Status.COMPLETED),
                    distinct=True,
                ),
            )
            .filter(
                total_lessons__gt=0,
                completed_lessons__lt=F('total_lessons'),
            )
            .prefetch_related(
                'modules',
                'modules__lessons',
            )
            .order_by('-updated_at')[:3]
        )

        serializer = ContinueLearningCourseSerializer(
            courses,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='summary',
    )
    def summary(self, request):
        courses = Course.objects.filter(
            owner=request.user,
        )

        active_courses = courses.filter(
            status=Course.Status.ACTIVE,
        ).count()

        courses_in_progress = (
            courses.filter(
                status=Course.Status.ACTIVE,
                modules__lessons__status=Lesson.Status.IN_PROGRESS,
            )
            .distinct()
            .count()
        )

        lessons_completed = Lesson.objects.filter(
            module__course__owner=request.user,
            status=Lesson.Status.COMPLETED,
        ).count()

        return Response(
            {
                'active_courses': active_courses,
                'courses_in_progress': courses_in_progress,
                'lessons_completed': lessons_completed,
            }
        )


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
