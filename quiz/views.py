from django.db.models import Count
from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from rest_framework import filters, viewsets
from rest_framework.exceptions import ValidationError

from .models import Choice, Exam, Question
from .serializers import (
    ChoiceResourceSerializer, ExamSerializer, QuestionSerializer,
    validate_option_state,
)


def document_resource(serializer):
    """Declare success and error responses in the executable OpenAPI contract."""
    errors = {401: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT}
    parameters = [OpenApiParameter(
        "exam", int, description="Solo las preguntas de este examen."
    )] if serializer is QuestionSerializer else []
    return extend_schema_view(
        list=extend_schema(parameters=parameters, responses={
            200: serializer(many=True), 400: OpenApiTypes.OBJECT, **errors,
        }),
        retrieve=extend_schema(responses={
            200: serializer, 404: OpenApiTypes.OBJECT, **errors,
        }),
        create=extend_schema(responses={
            201: serializer, 400: OpenApiTypes.OBJECT, **errors,
        }),
        update=extend_schema(responses={
            200: serializer, 400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT, **errors,
        }),
        partial_update=extend_schema(responses={
            200: serializer, 400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT, **errors,
        }),
        destroy=extend_schema(responses={
            204: None, 400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT, **errors,
        }),
    )


class AtomicWriteViewSet(viewsets.ModelViewSet):
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@document_resource(ExamSerializer)
class ExamViewSet(AtomicWriteViewSet):
    serializer_class = ExamSerializer
    queryset = Exam.objects.annotate(question_count=Count("questions")).order_by("id")


@document_resource(QuestionSerializer)
class QuestionViewSet(AtomicWriteViewSet):
    serializer_class = QuestionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]

    def get_queryset(self):
        queryset = Question.objects.select_related("exam").prefetch_related("choices")
        exam = self.request.query_params.get("exam")
        if exam is not None:
            if not exam.isdecimal() or int(exam) < 1:
                raise ValidationError({"exam": "Debe ser un entero positivo."})
            queryset = queryset.filter(exam_id=int(exam))
        return queryset


@document_resource(ChoiceResourceSerializer)
class ChoiceViewSet(AtomicWriteViewSet):
    serializer_class = ChoiceResourceSerializer
    queryset = Choice.objects.select_related("question").order_by("id")

    def perform_destroy(self, instance):
        flags = list(instance.question.choices.exclude(pk=instance.pk).values_list(
            "is_correct", flat=True
        ))
        validate_option_state(flags)
        instance.delete()
