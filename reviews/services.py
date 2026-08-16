import math
from datetime import timedelta

from django.utils import timezone

from .models import ReviewCard, ReviewLog

FIRST_INTERVAL_MINUTES = 10
ONE_DAY_MINUTES = 24 * 60
SIX_DAYS_MINUTES = 6 * 24 * 60
MAX_INTERVAL_MINUTES = 365 * 24 * 60
MIN_EASE_FACTOR = 1.3

EASE_DELTA = {
    ReviewLog.Grade.AGAIN: -0.2,
    ReviewLog.Grade.HARD: -0.15,
    ReviewLog.Grade.GOOD: 0,
    ReviewLog.Grade.EASY: 0.15,
}

MASTERED_INTERVAL_MINUTES = 30 * 24 * 60


def calculate_ease_factor(
    current_ease_factor: float,
    grade: str,
) -> float:
    return max(
        MIN_EASE_FACTOR,
        current_ease_factor + EASE_DELTA[grade],
    )


def calculate_long_term_interval(
    interval_minutes: int,
    ease_factor: float,
    grade: str,
) -> int:
    if grade == ReviewLog.Grade.HARD:
        value = interval_minutes * 1.2

    elif grade == ReviewLog.Grade.EASY:
        value = interval_minutes * ease_factor * 1.3

    else:
        value = interval_minutes * ease_factor

    # Same behaviour as JS Math.round() for positive values.
    rounded = math.floor(value + 0.5)

    return min(
        rounded,
        MAX_INTERVAL_MINUTES,
    )


def schedule_card(
    card: ReviewCard,
    grade: str,
    now=None,
) -> ReviewCard:
    if now is None:
        now = timezone.now()

    if grade == ReviewLog.Grade.AGAIN:
        card.interval_minutes = FIRST_INTERVAL_MINUTES
        card.repetitions = 0
        card.lapses += 1
        card.ease_factor = calculate_ease_factor(
            card.ease_factor,
            grade,
        )

    elif card.repetitions == 0:
        card.interval_minutes = FIRST_INTERVAL_MINUTES
        card.repetitions = 1

    else:
        if card.repetitions == 1:
            card.interval_minutes = ONE_DAY_MINUTES

        elif card.repetitions == 2:
            card.interval_minutes = SIX_DAYS_MINUTES

        else:
            card.interval_minutes = calculate_long_term_interval(
                card.interval_minutes,
                card.ease_factor,
                grade,
            )

        card.ease_factor = calculate_ease_factor(
            card.ease_factor,
            grade,
        )

        card.repetitions += 1

    card.due_at = now + timedelta(minutes=card.interval_minutes)

    return card


def get_card_status(card: ReviewCard) -> str:
    if card.repetitions == 0:
        if card.lapses > 0:
            return 'learning'

        return 'new'

    if card.repetitions < 3:
        return 'learning'

    if card.interval_minutes >= MASTERED_INTERVAL_MINUTES:
        return 'mastered'

    return 'review'


def is_card_due(
    card: ReviewCard,
    now=None,
) -> bool:
    if card.due_at is None:
        return False

    if now is None:
        now = timezone.now()

    return card.due_at <= now


def calculate_current_streak(
    activity_dates,
    today,
) -> int:
    dates = set(activity_dates)

    if today in dates:
        current_date = today
    elif today - timedelta(days=1) in dates:
        current_date = today - timedelta(days=1)
    else:
        return 0

    streak = 0

    while current_date in dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak
