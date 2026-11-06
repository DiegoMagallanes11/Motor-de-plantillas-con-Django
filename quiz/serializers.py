from django.db import transaction
from rest_framework import serializers

from .models import Choice, Exam, Question


class ChoiceSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if not attrs.get("text", "").strip():
            raise serializers.ValidationError({"text": "Este campo es requerido."})
        return attrs

    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]
        read_only_fields = ["id"]


class ExamSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    def get_question_count(self, obj) -> int:
        count = getattr(obj, "question_count", None)
        return count if count is not None else obj.questions.count()

    class Meta:
        model = Exam
        fields = ["id", "title", "created_at", "question_count"]
        read_only_fields = ["id", "created_at", "question_count"]


class QuestionSerializer(serializers.ModelSerializer):
    # Choices travel nested inside the question; the exam travels as an identifier.
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "exam", "text", "choices", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Una pregunta necesita al menos dos opciones.")
        if sum(1 for choice in value if choice.get("is_correct")) != 1:
            raise serializers.ValidationError("Debe haber exactamente una opción correcta.")
        return value

    def validate(self, attrs):
        if self.instance is None and "choices" not in attrs:
            raise serializers.ValidationError({"choices": "Este campo es requerido."})
        if self.instance is not None and "choices" not in attrs:
            choices = list(self.instance.choices.values("is_correct"))
            self.validate_choices(choices)
        return attrs

    def create(self, validated_data):
        choices = validated_data.pop("choices")
        with transaction.atomic():
            question = Question.objects.create(**validated_data)
            Choice.objects.bulk_create(Choice(question=question, **choice) for choice in choices)
        return question

    def update(self, instance, validated_data):
        choices = validated_data.pop("choices", None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if choices is not None:  # sent choices replace the old ones
                instance.choices.all().delete()
                Choice.objects.bulk_create(Choice(question=instance, **choice) for choice in choices)
        return instance


class ChoiceResourceSerializer(ChoiceSerializer):
    """Standalone option writes preserve the parent question's invariant."""

    class Meta(ChoiceSerializer.Meta):
        fields = ["id", "question", "text", "is_correct"]

    def validate(self, attrs):
        question = attrs.get("question") or getattr(self.instance, "question", None)
        if self.instance and question.pk != self.instance.question_id:
            raise serializers.ValidationError({"question": "No se puede mover una opción; edita la pregunta completa."})
        if question is None:
            raise serializers.ValidationError({"question": "Este campo es requerido."})
        existing = question.choices.all()
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        flags = list(existing.values_list("is_correct", flat=True))
        flags.append(attrs.get("is_correct", getattr(self.instance, "is_correct", False)))
        validate_option_state(flags)
        return attrs


def validate_option_state(flags):
    if len(flags) < 2 or sum(flags) != 1:
        raise serializers.ValidationError({
            "choices": "La pregunta debe conservar al menos dos opciones y exactamente una opción correcta."
        })
