from django.contrib import admin

from .models import Course, StudyArea


@admin.register(StudyArea)
class StudyAreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': {'name'}}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
