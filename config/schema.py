import strawberry

from config.mutations import Mutation
from config.types import CourseType
from learning.models import Course


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return 'Hello, world!'

    @strawberry.field
    def courses(self) -> list[CourseType]:
        return list(
            Course.objects.prefetch_related('modules__lessons').all()
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
