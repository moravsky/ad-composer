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

class PersonalizationTargetSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    text = serializers.CharField(required=True)

class WorkflowJobSerializer(serializers.Serializer):
    company_info_id = serializers.IntegerField(required=True)
    target_account_id = serializers.IntegerField(required=True)
    personalization_target = PersonalizationTargetSerializer(required=True)

class BatchPersonalizationRequestSerializer(serializers.Serializer):
    jobs = serializers.ListField(
        child=WorkflowJobSerializer(),
        required=True,
        min_length=1
    )
    
    def validate_jobs(self, value):
        if not value:
            raise serializers.ValidationError("At least one job must be provided")
        return value