from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from reviews.models import (
    ReviewCard,
    ReviewDeck,
    ReviewLog,
    ReviewTopic,
)

User = get_user_model()


class ReviewCardApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='denys@example.com',
            password='password123',
        )

        self.client.force_authenticate(
            user=self.user,
        )

        self.topic = ReviewTopic.objects.create(
            owner=self.user,
            name='Biology',
        )

        self.deck = ReviewDeck.objects.create(
            topic=self.topic,
            name='Cell Biology Basics',
        )

        self.card = ReviewCard.objects.create(
            deck=self.deck,
            question='What is a mitochondrion?',
            answer='An organelle that produces ATP.',
            hint='Think about energy.',
            difficulty=ReviewCard.Difficulty.MEDIUM,
            due_at=timezone.now() - timedelta(minutes=1),
        )

    def test_review_good_updates_card_and_creates_log(self):
        response = self.client.post(
            f'/api/review-cards/{self.card.id}/review/',
            {
                'grade': 'good',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.card.refresh_from_db()

        self.assertEqual(
            self.card.interval_minutes,
            10,
        )
        self.assertEqual(
            self.card.repetitions,
            1,
        )

        self.assertEqual(
            ReviewLog.objects.filter(
                card=self.card,
            ).count(),
            1,
        )

        log = ReviewLog.objects.get(
            card=self.card,
        )

        self.assertEqual(
            log.grade,
            ReviewLog.Grade.GOOD,
        )
        self.assertEqual(
            log.interval_before,
            0,
        )
        self.assertEqual(
            log.interval_after,
            10,
        )

    def test_review_before_due_time_returns_400(self):
        self.card.due_at = timezone.now() + timedelta(hours=1)
        self.card.save(update_fields=['due_at'])

        response = self.client.post(
            f'/api/review-cards/{self.card.id}/review/',
            {
                'grade': 'good',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            ReviewLog.objects.filter(card=self.card).count(),
            0,
        )

    def test_card_not_in_review_queue_returns_400(self):
        self.card.due_at = None
        self.card.save(update_fields=['due_at'])

        response = self.client.post(
            f'/api/review-cards/{self.card.id}/review/',
            {
                'grade': 'good',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data['detail'],
            'This card is not in the review queue.',
        )

    def test_due_endpoint_returns_only_due_cards(self):
        future_card = ReviewCard.objects.create(
            deck=self.deck,
            question='Future question',
            answer='Future answer',
            due_at=timezone.now() + timedelta(hours=1),
        )

        not_queued_card = ReviewCard.objects.create(
            deck=self.deck,
            question='Not queued',
            answer='Not queued answer',
            due_at=None,
        )

        response = self.client.get('/api/review-cards/due/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {item['id'] for item in response.data}

        self.assertIn(
            str(self.card.id),
            returned_ids,
        )

        self.assertNotIn(
            str(future_card.id),
            returned_ids,
        )

        self.assertNotIn(
            str(not_queued_card.id),
            returned_ids,
        )

    def test_user_cannot_review_another_users_card(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='password123',
        )

        other_topic = ReviewTopic.objects.create(
            owner=other_user,
            name='Other topic',
        )

        other_deck = ReviewDeck.objects.create(
            topic=other_topic,
            name='Other deck',
        )

        other_card = ReviewCard.objects.create(
            deck=other_deck,
            question='Private question',
            answer='Private answer',
            due_at=timezone.now() - timedelta(minutes=1),
        )

        response = self.client.post(
            f'/api/review-cards/{other_card.id}/review/',
            {
                'grade': 'good',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertEqual(
            ReviewLog.objects.filter(
                card=other_card,
            ).count(),
            0,
        )
