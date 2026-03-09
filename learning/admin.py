from django.contrib import admin

from .models import Course, Lesson, Module, StudyArea


@admin.register(StudyArea)
class StudyAreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'estimated_minutes')
    list_filter = ('module',)
    search_fields = ('title', 'description', 'content')
