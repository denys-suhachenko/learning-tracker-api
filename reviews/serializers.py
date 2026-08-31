from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import (
    ReviewCard,
    ReviewDeck,
    ReviewLog,
    ReviewTopic,
)
from .services import get_card_status, is_card_due


class ReviewGradeSerializer(serializers.Serializer):
    grade = serializers.ChoiceField(
        choices=ReviewLog.Grade.choices,
    )


class ReviewTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewTopic
        fields = (
            'id',
            'name',
            'created_at',
            'updated_at',
        )

        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
        )


class ReviewDeckSerializer(serializers.ModelSerializer):
    topic_id = serializers.PrimaryKeyRelatedField(
        source='topic',
        queryset=ReviewTopic.objects.none(),
    )

    class Meta:
        model = ReviewDeck
        fields = (
            'id',
            'topic_id',
            'name',
            'created_at',
            'updated_at',
        )

        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        if request and request.user.is_authenticated:
            self.fields['topic_id'].queryset = ReviewTopic.objects.filter(
                owner=request.user
            )


class ReviewCardSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    is_due = serializers.SerializerMethodField()

    deck_id = serializers.PrimaryKeyRelatedField(
        source='deck',
        queryset=ReviewDeck.objects.none(),
    )

    deck_name = serializers.CharField(
        source='deck.name',
        read_only=True,
    )

    topic_id = serializers.UUIDField(
        source='deck.topic.id',
        read_only=True,
    )

    topic_name = serializers.CharField(
        source='deck.topic.name',
        read_only=True,
    )

    review_next_session = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False,
    )

    class Meta:
        model = ReviewCard

        fields = (
            'id',
            'deck_id',
            'deck_name',
            'topic_id',
            'topic_name',
            'card_type',
            'question',
            'question_description',
            'answer',
            'answer_description',
            'hint',
            'difficulty',
            'review_next_session',
            'status',
            'is_due',
            'interval_minutes',
            'repetitions',
            'ease_factor',
            'lapses',
            'due_at',
            'created_at',
            'updated_at',
        )

        read_only_fields = (
            'id',
            'interval_minutes',
            'repetitions',
            'ease_factor',
            'lapses',
            'due_at',
            'created_at',
            'updated_at',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        if request and request.user.is_authenticated:
            self.fields['deck_id'].queryset = ReviewDeck.objects.filter(
                topic__owner=request.user
            )

    def validate_card_type(self, value):
        if value != ReviewCard.CardType.BASIC:
            raise serializers.ValidationError('Only basic cards are supported for now.')

        return value

    def validate_review_next_session(self, value):
        if self.instance is not None:
            raise serializers.ValidationError(
                'This field can only be used when creating a card.'
            )

        return value

    def create(self, validated_data):
        review_next_session = validated_data.pop(
            'review_next_session',
            False,
        )

        now = timezone.now()

        validated_data['due_at'] = (
            now if review_next_session else now + timedelta(days=1)
        )

        return super().create(validated_data)

    def get_status(self, obj):
        return get_card_status(obj)

    def get_is_due(self, obj):
        return is_card_due(obj)


class ReviewLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLog

        fields = (
            'id',
            'card',
            'grade',
            'reviewed_at',
            'interval_before',
            'interval_after',
        )

        read_only_fields = fields
