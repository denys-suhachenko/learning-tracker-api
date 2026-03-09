import uuid

from django.db import models
from django.db.models import Max


class StudyArea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'active', 'Active'

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    study_area = models.ForeignKey(
        StudyArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'order'],
                name='unique_module_order_within_course',
            )
        ]

    def save(self, *args, **kwargs):
        if self.order is None:
            max_order = (
                Module.objects.filter(course=self.course)
                .aggregate(max_order=Max('order'))
                .get('max_order')
            )
            self.order = 1 if max_order is None else max_order + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} / {self.course.title}'


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    estimated_minutes = models.PositiveIntegerField(default=15)

    class Meta:
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['module', 'order'],
                name='unique_lesson_order_within_module',
            )
        ]

    def save(self, *args, **kwargs):
        if self.order is None:
            max_order = (
                Lesson.objects.filter(module=self.module)
                .aggregate(max_order=Max('order'))
                .get('max_order')
            )
            self.order = 1 if max_order is None else max_order + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} / {self.module.title}'
