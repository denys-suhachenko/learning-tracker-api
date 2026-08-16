import strawberry

from learning.models import Course, Lesson

from .types import (
    CourseCreateInput,
    CourseType,
    CourseUpdateInput,
    LessonCreateInput,
    LessonType,
    LessonUpdateInput,
)


def _apply(instance, input):
    for field, value in vars(input).items():
        if value is not strawberry.UNSET and value is not None:
            setattr(instance, field, value)
    return instance


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_course(self, input: CourseCreateInput) -> CourseType:
        return Course.objects.create(
            title=input.title,
            slug=input.slug,
            description=input.description,
            owner_id=input.owner_id,
            study_area_id=input.study_area_id,
            status=input.status,
        )

    @strawberry.mutation
    def update_course(self, id: strawberry.ID, input: CourseUpdateInput) -> CourseType:
        course = Course.objects.get(id=id)
        _apply(course, input)
        course.save()
        return course

    @strawberry.mutation
    def create_lesson(self, input: LessonCreateInput) -> LessonType:
        # order is intentionally not settable here - Lesson.save() auto-fills
        # it from the max order within the module when order is None.
        return Lesson.objects.create(
            module_id=input.module_id,
            title=input.title,
            description=input.description,
            content=input.content,
            estimated_minutes=input.estimated_minutes,
            status=input.status,
        )

    @strawberry.mutation
    def update_lesson(self, id: strawberry.ID, input: LessonUpdateInput) -> LessonType:
        lesson = Lesson.objects.get(id=id)
        _apply(lesson, input)
        lesson.save()
        return lesson
