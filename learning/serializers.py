from rest_framework import serializers

from .models import Course, Lesson, Module, StudyArea


class StudyAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyArea
        fields = ('id', 'name', 'slug')


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id',
            'title',
            'description',
            'content',
            'order',
            'estimated_minutes',
        )


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = (
            'id',
            'title',
            'description',
            'order',
            'lessons',
        )


class CourseListSerializer(serializers.ModelSerializer):
    study_area = StudyAreaSerializer(read_only=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'slug',
            'description',
            'status',
            'study_area',
        )


class CourseDetailSerializer(serializers.ModelSerializer):
    study_area = StudyAreaSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'slug',
            'description',
            'status',
            'study_area',
            'modules',
            'created_at',
            'updated_at',
        )
