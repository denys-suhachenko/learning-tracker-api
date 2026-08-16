from rest_framework.routers import DefaultRouter

from .views import (
    ReviewCardViewSet,
    ReviewDeckViewSet,
    ReviewLogViewSet,
    ReviewTopicViewSet,
)

router = DefaultRouter()

router.register(
    'review-topics',
    ReviewTopicViewSet,
    basename='review-topic',
)

router.register(
    'review-decks',
    ReviewDeckViewSet,
    basename='review-deck',
)

router.register(
    'review-cards',
    ReviewCardViewSet,
    basename='review-card',
)

router.register(
    'review-logs',
    ReviewLogViewSet,
    basename='review-log',
)

urlpatterns = router.urls
