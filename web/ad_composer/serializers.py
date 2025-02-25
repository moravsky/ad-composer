from rest_framework import serializers

class PersonalizationRequestSerializer(serializers.Serializer):
    """
    Serializer for validating personalization requests.
    """
    client = serializers.CharField(required=True, max_length=255)
    texts = serializers.ListField(
        child=serializers.CharField(max_length=5000),
        required=True,
        min_length=1
    )

class PersonalizationResponseSerializer(serializers.Serializer):
    """
    Serializer for formatting personalization responses.
    """
    client = serializers.CharField()
    originalTexts = serializers.ListField(child=serializers.CharField())
    personalizedContent = serializers.ListField(child=serializers.CharField())