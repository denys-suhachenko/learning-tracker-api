from rest_framework import serializers
from .models import StudyArea, Course, Module, Lesson


class StudyAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyArea
        fields = ('id', 'name', 'slug')


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id',
            'module',
            'title',
            'description',
            'content',
            'order',
            'estimated_minutes',
        )


class LessonNestedSerializer(LessonSerializer):
    class Meta(LessonSerializer.Meta):
        fields = (
            'id',
            'title',
            'description',
            'order',
            'estimated_minutes',
        )


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = (
            'id',
            'course',
            'title',
            'description',
            'order',
        )


class ModuleDetailSerializer(ModuleSerializer):
    lessons = LessonNestedSerializer(many=True, read_only=True)

    class Meta(ModuleSerializer.Meta):
        fields = ModuleSerializer.Meta.fields + ('lessons',)


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'slug',
            'description',
            'study_area',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')


class CourseDetailSerializer(CourseSerializer):
    study_area = StudyAreaSerializer(read_only=True)
    modules = ModuleDetailSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
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
