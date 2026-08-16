from datetime import datetime, time, timedelta

from django.db import transaction
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import (
    ReviewCard,
    ReviewDeck,
    ReviewLog,
    ReviewTopic,
)
from .serializers import (
    ReviewCardSerializer,
    ReviewDeckSerializer,
    ReviewGradeSerializer,
    ReviewLogSerializer,
    ReviewTopicSerializer,
)
from .services import (
    MASTERED_INTERVAL_MINUTES,
    calculate_current_streak,
    schedule_card,
)


class ReviewTopicViewSet(ModelViewSet):
    serializer_class = ReviewTopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewTopic.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReviewDeckViewSet(ModelViewSet):
    serializer_class = ReviewDeckSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewDeck.objects.filter(topic__owner=self.request.user).select_related(
            'topic'
        )


class ReviewCardViewSet(ModelViewSet):
    serializer_class = ReviewCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            ReviewCard.objects.filter(deck__topic__owner=self.request.user)
            .select_related(
                'deck',
                'deck__topic',
            )
            .filter(
                deck__topic__owner=self.request.user,
                is_archived=False,
            )
        )

        status = self.request.query_params.get('status')
        due = self.request.query_params.get('due')
        topic_id = self.request.query_params.get('topic')
        deck_id = self.request.query_params.get('deck')
        search = self.request.query_params.get('search')

        if status == 'new':
            queryset = queryset.filter(
                repetitions=0,
                lapses=0,
            )

        elif status == 'learning':
            queryset = queryset.filter(
                Q(
                    repetitions__in=(1, 2),
                )
                | Q(
                    repetitions=0,
                    lapses__gt=0,
                )
            )

        elif status == 'review':
            queryset = queryset.filter(
                repetitions__gte=3,
                interval_minutes__lt=MASTERED_INTERVAL_MINUTES,
            )

        elif status == 'mastered':
            queryset = queryset.filter(
                repetitions__gte=3,
                interval_minutes__gte=MASTERED_INTERVAL_MINUTES,
            )

        if due == 'true':
            queryset = queryset.filter(
                due_at__isnull=False,
                due_at__lte=timezone.now(),
            )

        if topic_id:
            queryset = queryset.filter(
                deck__topic_id=topic_id,
            )

        if deck_id:
            queryset = queryset.filter(
                deck_id=deck_id,
            )

        if search:
            queryset = queryset.filter(
                Q(question__icontains=search)
                | Q(answer__icontains=search)
                | Q(hint__icontains=search)
            )

        return queryset

    @action(
        detail=False,
        methods=['get'],
        url_path='due',
    )
    def due(self, request):
        now = timezone.now()

        cards = (
            self.get_queryset()
            .filter(
                due_at__isnull=False,
                due_at__lte=now,
            )
            .order_by('due_at')
        )

        serializer = self.get_serializer(
            cards,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        url_path='review',
    )
    def review(self, request, pk=None):
        grade_serializer = ReviewGradeSerializer(
            data=request.data,
        )

        grade_serializer.is_valid(
            raise_exception=True,
        )

        grade = grade_serializer.validated_data['grade']
        now = timezone.now()

        with transaction.atomic():
            card = get_object_or_404(
                self.get_queryset().select_for_update(),
                pk=pk,
            )

            if card.due_at is None:
                return Response(
                    {'detail': ('This card is not in the review queue.')},
                    status=400,
                )

            if card.due_at > now:
                return Response(
                    {
                        'detail': 'This card is not due yet.',
                        'due_at': card.due_at,
                    },
                    status=400,
                )

            interval_before = card.interval_minutes

            schedule_card(
                card=card,
                grade=grade,
                now=now,
            )

            card.save()

            ReviewLog.objects.create(
                card=card,
                grade=grade,
                reviewed_at=now,
                interval_before=interval_before,
                interval_after=card.interval_minutes,
            )

        return Response(self.get_serializer(card).data)

    @action(
        detail=False,
        methods=['get'],
        url_path='summary',
    )
    def summary(self, request):
        now = timezone.now()
        today = timezone.localdate()
        current_timezone = timezone.get_current_timezone()

        tomorrow = today + timedelta(days=1)

        day_start = timezone.make_aware(
            datetime.combine(today, time.min),
            current_timezone,
        )

        next_day_start = timezone.make_aware(
            datetime.combine(tomorrow, time.min),
            current_timezone,
        )

        cards = self.get_queryset()

        new_cards = cards.filter(
            repetitions=0,
            lapses=0,
        ).count()

        learning = cards.filter(
            Q(repetitions__in=(1, 2))
            | Q(
                repetitions=0,
                lapses__gt=0,
            )
        ).count()

        mastered_cards = cards.filter(
            repetitions__gte=3,
            interval_minutes__gte=MASTERED_INTERVAL_MINUTES,
        ).count()

        due_now = cards.filter(
            due_at__isnull=False,
            due_at__lte=now,
        ).count()

        due_today = cards.filter(
            due_at__gte=day_start,
            due_at__lt=next_day_start,
        ).count()

        review_logs = ReviewLog.objects.filter(card__deck__topic__owner=request.user)

        reviewed_today = review_logs.filter(
            reviewed_at__gte=day_start,
            reviewed_at__lt=next_day_start,
        ).count()

        activity_dates = set(
            review_logs.annotate(
                review_date=TruncDate(
                    'reviewed_at',
                    tzinfo=current_timezone,
                )
            )
            .values_list(
                'review_date',
                flat=True,
            )
            .distinct()
        )

        current_streak = calculate_current_streak(
            activity_dates=activity_dates,
            today=today,
        )

        week_start = today - timedelta(days=today.weekday())

        week_activity = []

        for day_offset in range(7):
            day = week_start + timedelta(days=day_offset)

            week_activity.append(
                {
                    'date': day.isoformat(),
                    'is_active': day in activity_dates,
                    'is_future': day > today,
                }
            )

        return Response(
            {
                'due_now': due_now,
                'due_today': due_today,
                'reviewed_today': reviewed_today,
                'new_cards': new_cards,
                'learning': learning,
                'mastered_cards': mastered_cards,
                'current_streak': current_streak,
                'week_activity': week_activity,
            }
        )

    def destroy(self, request, *args, **kwargs):
        card = self.get_object()

        card.is_archived = True
        card.due_at = None
        card.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ReviewLogViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = ReviewLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewLog.objects.filter(
            card__deck__topic__owner=self.request.user
        ).select_related(
            'card',
            'card__deck',
            'card__deck__topic',
        )
