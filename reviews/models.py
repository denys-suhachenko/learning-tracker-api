import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ReviewTopic(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_topics',
    )

    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ReviewDeck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    topic = models.ForeignKey(
        ReviewTopic,
        on_delete=models.CASCADE,
        related_name='decks',
    )

    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ReviewCard(models.Model):
    class CardType(models.TextChoices):
        BASIC = 'basic', 'Basic'
        CLOZE = 'cloze', 'Cloze'
        IMAGE_OCCLUSION = 'image_occlusion', 'Image occlusion'
        QA = 'qa', 'Q&A'

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    deck = models.ForeignKey(
        ReviewDeck,
        on_delete=models.CASCADE,
        related_name='cards',
    )

    card_type = models.CharField(
        max_length=20,
        choices=CardType.choices,
        default=CardType.BASIC,
    )

    question = models.TextField()
    question_description = models.TextField(
        blank=True,
        default='',
    )

    answer = models.TextField()
    answer_description = models.TextField(
        blank=True,
        default='',
    )

    hint = models.TextField(blank=True)

    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
    )

    interval_minutes = models.PositiveIntegerField(default=0)
    repetitions = models.PositiveIntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)
    lapses = models.PositiveIntegerField(default=0)

    due_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_archived = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question[:50]


class ReviewLog(models.Model):
    class Grade(models.TextChoices):
        AGAIN = 'again', 'Again'
        HARD = 'hard', 'Hard'
        GOOD = 'good', 'Good'
        EASY = 'easy', 'Easy'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    card = models.ForeignKey(
        ReviewCard,
        on_delete=models.CASCADE,
        related_name='review_logs',
    )

    grade = models.CharField(
        max_length=10,
        choices=Grade.choices,
    )

    reviewed_at = models.DateTimeField(
        default=timezone.now,
    )

    interval_before = models.PositiveIntegerField()
    interval_after = models.PositiveIntegerField()

    class Meta:
        ordering = ['-reviewed_at']

    def __str__(self):
        return f'{self.card_id} - {self.grade}'
