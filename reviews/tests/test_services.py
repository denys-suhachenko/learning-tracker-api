from datetime import datetime, timedelta

from django.test import SimpleTestCase
from django.utils import timezone

from reviews.models import ReviewCard, ReviewLog
from reviews.services import schedule_card


class ScheduleCardTests(SimpleTestCase):
    def setUp(self):
        self.now = timezone.make_aware(datetime(2026, 8, 12, 12, 0))

    def create_card(self, **kwargs):
        defaults = {
            'question': 'Question',
            'answer': 'Answer',
            'interval_minutes': 0,
            'repetitions': 0,
            'ease_factor': 2.5,
            'lapses': 0,
            'due_at': self.now,
        }

        defaults.update(kwargs)

        return ReviewCard(**defaults)

    def test_new_card_good_schedules_10_minutes(self):
        card = self.create_card()

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.GOOD,
            now=self.now,
        )

        self.assertEqual(card.interval_minutes, 10)
        self.assertEqual(card.repetitions, 1)
        self.assertEqual(card.ease_factor, 2.5)
        self.assertEqual(card.lapses, 0)
        self.assertEqual(
            card.due_at,
            self.now + timedelta(minutes=10),
        )

    def test_second_good_schedules_one_day(self):
        card = self.create_card(
            interval_minutes=10,
            repetitions=1,
        )

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.GOOD,
            now=self.now,
        )

        self.assertEqual(card.interval_minutes, 24 * 60)
        self.assertEqual(card.repetitions, 2)
        self.assertEqual(card.ease_factor, 2.5)
        self.assertEqual(
            card.due_at,
            self.now + timedelta(days=1),
        )

    def test_third_good_schedules_six_days(self):
        card = self.create_card(
            interval_minutes=24 * 60,
            repetitions=2,
        )

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.GOOD,
            now=self.now,
        )

        self.assertEqual(
            card.interval_minutes,
            6 * 24 * 60,
        )
        self.assertEqual(card.repetitions, 3)
        self.assertEqual(card.ease_factor, 2.5)
        self.assertEqual(
            card.due_at,
            self.now + timedelta(days=6),
        )

    def test_again_resets_card_to_learning(self):
        card = self.create_card(
            interval_minutes=6 * 24 * 60,
            repetitions=3,
            ease_factor=2.5,
            lapses=0,
        )

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.AGAIN,
            now=self.now,
        )

        self.assertEqual(card.interval_minutes, 10)
        self.assertEqual(card.repetitions, 0)
        self.assertEqual(card.lapses, 1)
        self.assertAlmostEqual(card.ease_factor, 2.3)
        self.assertEqual(
            card.due_at,
            self.now + timedelta(minutes=10),
        )

    def test_hard_in_long_term_review_increases_interval_by_20_percent(self):
        card = self.create_card(
            interval_minutes=6 * 24 * 60,
            repetitions=3,
            ease_factor=2.5,
        )

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.HARD,
            now=self.now,
        )

        self.assertEqual(
            card.interval_minutes,
            10368,
        )
        self.assertEqual(card.repetitions, 4)
        self.assertAlmostEqual(card.ease_factor, 2.35)

    def test_easy_in_long_term_review_uses_easy_bonus(self):
        card = self.create_card(
            interval_minutes=6 * 24 * 60,
            repetitions=3,
            ease_factor=2.5,
        )

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.EASY,
            now=self.now,
        )

        self.assertEqual(
            card.interval_minutes,
            28080,
        )
        self.assertEqual(card.repetitions, 4)
        self.assertAlmostEqual(card.ease_factor, 2.65)

    def test_ease_factor_never_goes_below_minimum(self):
        card = self.create_card(
            interval_minutes=6 * 24 * 60,
            repetitions=3,
            ease_factor=1.35,
            lapses=0,
        )

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.AGAIN,
            now=self.now,
        )

        self.assertAlmostEqual(card.ease_factor, 1.3)

    def test_interval_never_exceeds_one_year(self):
        card = self.create_card(
            interval_minutes=300 * 24 * 60,
            repetitions=5,
            ease_factor=2.5,
        )

        schedule_card(
            card=card,
            grade=ReviewLog.Grade.GOOD,
            now=self.now,
        )

        max_interval = 365 * 24 * 60

        self.assertEqual(
            card.interval_minutes,
            max_interval,
        )

        self.assertEqual(
            card.due_at,
            self.now + timedelta(days=365),
        )
