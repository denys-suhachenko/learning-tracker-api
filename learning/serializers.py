from rest_framework import serializers

from .models import Course, Lesson, Module, StudyArea


class StudyAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyArea
        fields = ('id', 'name', 'slug')


class LessonSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all())

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
            'status',
        )


class LessonNestedSerializer(LessonSerializer):
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
            'status',
        )


class ModuleSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        source='course',
        queryset=Course.objects.all(),
    )

    class Meta:
        model = Module
        fields = (
            'id',
            'course_id',
            'title',
            'description',
            'order',
        )


class ModuleNestedSerializer(serializers.ModelSerializer):
    lessons = LessonNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = (
            'id',
            'title',
            'order',
            'lessons',
        )


class ModuleDetailSerializer(ModuleSerializer):
    course_id = serializers.UUIDField(read_only=True)
    lessons = LessonNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = (
            'id',
            'course_id',
            'title',
            'description',
            'order',
            'lessons',
        )


class CourseSerializer(serializers.ModelSerializer):
    study_area = serializers.PrimaryKeyRelatedField(
        queryset=StudyArea.objects.all(),
        allow_null=True,
    )

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['study_area'] = (
            StudyAreaSerializer(instance.study_area).data
            if instance.study_area_id
            else None
        )
        return data


class CourseDetailSerializer(CourseSerializer):
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


class CourseReadSerializer(serializers.ModelSerializer):
    study_area = StudyAreaSerializer()

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


class CourseDetailReadSerializer(CourseReadSerializer):
    modules = ModuleDetailSerializer(many=True)

    class Meta(CourseReadSerializer.Meta):
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
