from rest_framework import serializers
from .models import CompanyInfo

class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = '__all__'

class PersonalizationRequestSerializer(serializers.Serializer):
    client = serializers.CharField(required=True)
    texts = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        min_length=1
    )
    
    def validate_texts(self, value):
        if not all(value):
            raise serializers.ValidationError("All texts must be non-empty")
        return value

class PersonalizationResponseSerializer(serializers.Serializer):
    client = serializers.CharField()
    originalTexts = serializers.ListField(child=serializers.CharField())
    personalizedContent = serializers.ListField(child=serializers.CharField())