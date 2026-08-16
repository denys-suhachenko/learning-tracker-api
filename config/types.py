from datetime import datetime

import strawberry

from learning.models import Course, Lesson


@strawberry.type
class LessonType:
    id: strawberry.ID
    title: str
    description: str
    content: str
    order: int
    estimated_minutes: int
    status: str
    module_id: strawberry.ID


@strawberry.type
class ModuleType:
    id: strawberry.ID
    title: str
    description: str
    order: int
    course_id: strawberry.ID

    @strawberry.field
    def lessons(self) -> list[LessonType]:
        return list(self.lessons.all())


@strawberry.type
class CourseType:
    id: strawberry.ID
    title: str
    slug: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    owner_id: strawberry.ID
    study_area_id: strawberry.ID | None
    progress: int

    @strawberry.field
    def modules(self) -> list[ModuleType]:
        return list(self.modules.all())


@strawberry.input
class CourseCreateInput:
    title: str
    slug: str
    owner_id: strawberry.ID
    description: str = ''
    study_area_id: strawberry.ID | None = None
    status: str = Course.Status.DRAFT


@strawberry.input
class CourseUpdateInput:
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    study_area_id: strawberry.ID | None = None
    status: str | None = None


@strawberry.input
class LessonCreateInput:
    module_id: strawberry.ID
    title: str
    description: str = ''
    content: str = ''
    estimated_minutes: int = 15
    status: str = Lesson.Status.PLANNED


@strawberry.input
class LessonUpdateInput:
    title: str | None = None
    description: str | None = None
    content: str | None = None
    estimated_minutes: int | None = None
    status: str | None = None
