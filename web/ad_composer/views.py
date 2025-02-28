import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from urllib.parse import urljoin, urlparse
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
@csrf_exempt
def personalize_content(request):
    """
    POST endpoint to personalize marketing content using OpenAI and LangChain.
    Takes 'client' (target account) and 'texts' in the request body.
    Personalizes Stmapli content for the target account.
    """
    # Validate request data using serializer
    serializer = PersonalizationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get validated data
    target_account = serializer.validated_data['client']
    texts = serializer.validated_data['texts']
    
    try:
        # Get company info (Stmapli) from database
        company_info = CompanyInfo.objects.first()
        if not company_info:
            logger.error("No company information found for Stmapli")
            return Response(
                {"error": "No company information found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get target account details
        target = Account.objects.filter(name=target_account).first()
        if not target:
            logger.error(f"Target account not found: {target_account}")
            return Response(
                {"error": f"Target account not found: {target_account}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get target account context from their website if available
        target_context = ""
        if target and target.url:
            target_context = get_contextual_information(target.url)
            logger.info(f"Retrieved context for target account: {target_account}")
        
        # Use LangChain's ChatOpenAI for personalization
        chat_model = ChatOpenAI(
            model="gpt-3.5-turbo", 
            temperature=0.7, 
            max_tokens=1000
        )
        
        # Generate personalized content
        personalized_texts = []
        for text in texts:
            # Enhanced prompt with both company and target information
            prompt = f"""
            You are a marketing expert specializing in personalized B2B content creation.
            
            Your company (content creator): {company_info.company_name}
            Your company description: {company_info.company_description}
            
            Target client: {target_account}
            Target client's website context: {target_context}
            
            Original Marketing Text: {text}
            
            Personalization Guidelines:
            - Keep the personalized text consise and rougly the same length as the original marketing text
            - Tailor our ({company_info.company_name}) content specifically for {target_account}'s needs and challenges
            - Maintain a professional B2B tone while being compelling and relevant
            - Don't add quotes unless original text contains quotes
            
            Personalized version:
            """
            
            response = chat_model.invoke(prompt)
            personalized_texts.append(response.content)
            logger.info(f"Generated personalized content for text #{len(personalized_texts)}")
        
        # Prepare response data
        response_data = {
            "client": target_account,
            "originalTexts": texts,
            "personalizedContent": personalized_texts
        }
        
        # Validate and return response
        response_serializer = PersonalizationResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data)
        else:
            logger.error(f"Response validation error: {response_serializer.errors}")
            return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Personalization error: {e}")
        return Response({
            "error": "Failed to personalize content",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def get_contextual_information(url):
    try:
        # Load webpage content
        loader = WebBaseLoader(url)
        documents = loader.load()
        
        # Log raw document content
        logger.info(f"Raw document content length: {len(documents[0].page_content)} characters")
        print(f"Raw Document Content (first 500 chars):\n{documents[0].page_content[:500]}")
        
        # Split content into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        # Log split texts
        logger.info(f"Number of text chunks: {len(texts)}")
        print("\nText Chunks:")
        for i, chunk in enumerate(texts[:5], 1):  # Print first 5 chunks
            print(f"\nChunk {i} (length {len(chunk.page_content)}):")
            print(chunk.page_content[:500])  # Print first 500 chars of each chunk
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(texts, embeddings)
        
        # Create retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            ChatOpenAI(temperature=0), 
            chain_type="stuff", 
            retriever=vectorstore.as_retriever()
        )
        
        # Query for relevant context
        context_query = "Extract the key messaging, brand positioning, and main pain points of this company"
        context = qa_chain.run(context_query)
        
        # Log and print extracted context
        logger.info(f"Extracted Context:\n{context}")
        print(f"\nExtracted Context:\n{context}")
        
        return context
    
    except Exception as e:
        logger.error(f"Error retrieving contextual information: {e}")
        print(f"Error: {e}")
        return ""