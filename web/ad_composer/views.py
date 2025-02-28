import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from urllib.parse import urljoin, urlparse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import re
import requests
from .models import Account, CompanyInfo
from .serializers import PersonalizationRequestSerializer, PersonalizationResponseSerializer
import openai

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_account_names(request):
    """
    GET endpoint to retrieve account names from the database.
    Returns a list of account names.
    """
    try:
        # Use Django ORM instead of raw SQL
        account_names = Account.objects.values_list('name', flat=True)
        return Response(list(account_names))
    
    except Exception as e:
        logger.error(f"Error retrieving account names: {e}")
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def fetch_url(request):
    url = request.GET.get('url')
    try:
        # Fetch the page content
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        # Get the base URL for resolving relative URLs
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # Modify HTML to make URLs absolute
        content = response.text
        
        # Replace src attributes
        content = re.sub(
            r'(src=["\']\/)([^"\']+)',
            lambda m: f'src="{urljoin(base_url, m.group(1) + m.group(2))}"',
            content
        )
        
        # Replace href attributes
        content = re.sub(
            r'(href=["\']\/)([^"\']+)',
            lambda m: f'href="{urljoin(base_url, m.group(1) + m.group(2))}"',
            content
        )
        
        # Return the modified HTML directly
        return HttpResponse(content, content_type='text/html')
    
    except requests.RequestException as e:
        return HttpResponse(f'Error: {str(e)}', status=400)
    
def index(request):
    return render(request, 'ad_composer/index.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def get_company_info(request):
    """
    GET endpoint to retrieve company information from the database.
    """
    try:
        # Get the first company info record, since we only have one rn
        company_info = CompanyInfo.objects.first()
        
        if not company_info:
            return Response(
                {"error": "No company information found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        from .serializers import CompanyInfoSerializer
        serializer = CompanyInfoSerializer(company_info)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error retrieving company info: {e}")
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def personalize_content(request):
    """
    POST endpoint to personalize marketing content using OpenAI.
    Requires 'client' and 'texts' in the request body.
    """
    # Validate request data using serializer
    serializer = PersonalizationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get validated data
    client = serializer.validated_data['client']
    texts = serializer.validated_data['texts']
    
    try:
        # Try to get account details from database to enhance prompt
        account = Account.objects.filter(name=client).first()
        account_context = f"Account URL: {account.url}" if account else ""
        
        # Construct personalization prompt
        prompt = f"""
            You are a marketing expert specializing in personalized content creation.
            
            Client: {client}
            {account_context}
            
            Personalize the following texts to make them more appealing and relevant to {client}:
            
            {chr(10).join([f"Text {i + 1}: {text}" for i, text in enumerate(texts)])}
            
            Please return ONLY the personalized text for each input, without any additional explanation.

            Don't add quotes unless original text contains quotes.
        """
        
        # Call OpenAI API
        client_openai = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        completion = client_openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful marketing expert specializing in content personalization. Return only the personalized text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Get the full content
        full_content = completion.choices[0].message.content
        logger.debug(f'Full OpenAI Response: {full_content}')
        
        # Extract personalized texts
        personalized_texts = []
        for i in range(len(texts)):
            lines = full_content.split('\n')
            target_line = next((line for line in lines if line.startswith(f"Text {i + 1}:")), None)
            
            if target_line:
                # Remove the "Text X:" prefix and trim
                personalized_text = target_line.replace(f"Text {i + 1}:", '').strip()
                logger.error(f"personalized_text: {personalized_text}")
                personalized_texts.append(personalized_text)
            else:
                personalized_texts.append('')
        
        # Prepare and validate response using serializer
        response_data = {
            "client": client,
            "originalTexts": texts,
            "personalizedContent": personalized_texts
        }
        
        response_serializer = PersonalizationResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data)
        else:
            # This shouldn't normally happen, but just in case
            logger.error(f"Response validation error: {response_serializer.errors}")
            return JsonResponse(response_data, safe=False)
        
    except Exception as e:
        logger.error(f"Personalization error: {e}")
        return Response({
            "error": "Failed to personalize content",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)