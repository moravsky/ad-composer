#!/usr/bin/env python3
"""
Activities for the target workflow.
"""
import logging
import os
import yaml
from datetime import timedelta, datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import psycopg2
from psycopg2.extras import RealDictCursor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI

from temporalio import activity

logger = logging.getLogger(__name__)

# Define dataclasses for activity parameters
@dataclass
class PersonalizeContentInput:
    """Input parameters for generate_personalized_content_activity."""
    company_info: Dict[str, Any]
    target_account: Dict[str, Any]
    target_context: str
    text: str
    text_type: str

@dataclass
class SaveContentInput:
    """Input parameters for save_personalized_content_activity."""
    company_info_id: int
    target_account_id: int
    original_text: str
    personalized_text: str
    text_type: str

# Load configuration
def _load_config():
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "config", "target_workflow_config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# Database connection
def _get_db_connection():
    """Get a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "addb"),
        user=os.environ.get("DB_USER", "ad_user"),
        password=os.environ.get("DB_PASSWORD", "your_secure_password")
    )

def _serialize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert datetime objects to ISO format strings in a dictionary."""
    if data is None:
        return None
    
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

@activity.defn
async def get_company_info_activity(company_info_id: int) -> Dict[str, Any]:
    """
    Get company information from the database.
    
    Args:
        company_info_id: ID of the company info to retrieve
        
    Returns:
        Dictionary with company information
    """
    activity.logger.info(f"Getting company info for ID: {company_info_id}")
    
    try:
        with _get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM company_info WHERE id = %s",
                    (company_info_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    activity.logger.info(f"Found company info: {result['company_name']}")
                    return _serialize_dict(dict(result))
                else:
                    activity.logger.warning(f"No company info found for ID: {company_info_id}")
                    return None
    except Exception as e:
        activity.logger.error(f"Error getting company info: {str(e)}")
        raise

@activity.defn
async def get_target_account_activity(target_account_id: int) -> Dict[str, Any]:
    """
    Get target account information from the database.
    
    Args:
        target_account_id: ID of the target account to retrieve
        
    Returns:
        Dictionary with target account information
    """
    activity.logger.info(f"Getting target account for ID: {target_account_id}")
    
    try:
        with _get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM accounts WHERE id = %s",
                    (target_account_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    activity.logger.info(f"Found target account: {result['name']}")
                    return _serialize_dict(dict(result))
                else:
                    activity.logger.warning(f"No target account found for ID: {target_account_id}")
                    return None
    except Exception as e:
        activity.logger.error(f"Error getting target account: {str(e)}")
        raise

@activity.defn
async def get_contextual_information_activity(url: str) -> str:
    """
    Get contextual information from a target's website.
    
    Args:
        url: URL of the target's website
        
    Returns:
        String with contextual information
    """
    activity.logger.info(f"Getting contextual information from URL: {url}")
    
    try:
        # Load webpage content
        loader = WebBaseLoader(url)
        documents = loader.load()
        
        # Log raw document content
        activity.logger.info(f"Raw document content length: {len(documents[0].page_content)} characters")
        
        # Split content into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        # Log split texts
        activity.logger.info(f"Number of text chunks: {len(texts)}")
        
        # Create embeddings and vector store
        config = _load_config()
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vectorstore = Chroma.from_documents(texts, embeddings)
        
        # Create retrieval chain
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        qa_chain = RetrievalQA.from_chain_type(
            ChatOpenAI(temperature=0, openai_api_key=openai_api_key),
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        
        # Query for relevant context
        context_query = "Extract the key messaging, brand positioning, and main pain points of this company"
        context = qa_chain.run(context_query)
        
        # Log extracted context
        activity.logger.info(f"Extracted Context:\n{context}")
        
        return context
    
    except Exception as e:
        activity.logger.error(f"Error retrieving contextual information: {str(e)}")
        return ""

@activity.defn
async def generate_personalized_content_activity(input_params: PersonalizeContentInput) -> str:
    """
    Generate personalized content using OpenAI.
    
    Args:
        input_params: PersonalizeContentInput containing:
            - company_info: Dictionary with company information
            - target_account: Dictionary with target account information
            - target_context: String with contextual information about the target
            - text: Original text to personalize
            - text_type: Type of text (e.g., "email", "ad", "social")
        
    Returns:
        String with personalized content
    """
    activity.logger.info(f"Generating personalized content for {input_params.target_account['name']}, type: {input_params.text_type}")
    
    try:
        # Load OpenAI settings from config
        config = _load_config()
        openai_config = config.get("openai", {})
        
        # Use LangChain's ChatOpenAI for personalization
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        chat_model = ChatOpenAI(
            model=openai_config.get("model", "gpt-3.5-turbo"),
            temperature=openai_config.get("temperature", 0.7),
            max_tokens=openai_config.get("max_tokens", 1000),
            openai_api_key=openai_api_key
        )
        
        # Enhanced prompt with both company and target information
        prompt = f"""
        You are a marketing expert specializing in personalized B2B content creation.
        
        Your company (content creator): {input_params.company_info['company_name']}
        Your company description: {input_params.company_info['company_description']}
        
        Target client: {input_params.target_account['name']}
        Target client's website context: {input_params.target_context}
        
        Content type: {input_params.text_type}
        Original Text: {input_params.text}
        
        Personalization Guidelines:
        - Keep the personalized text concise and roughly the same length as the original text
        - Tailor our ({input_params.company_info['company_name']}) content specifically for {input_params.target_account['name']}'s needs and challenges
        - Maintain a professional B2B tone while being compelling and relevant
        - Don't add quotes unless original text contains quotes
        - Adapt the content to be appropriate for the content type: {input_params.text_type}
        
        Personalized version:
        """
        
        response = chat_model.invoke(prompt)
        personalized_text = response.content
        
        activity.logger.info(f"Generated personalized content for {input_params.target_account['name']}")
        return personalized_text
    
    except Exception as e:
        activity.logger.error(f"Error generating personalized content: {str(e)}")
        raise

@activity.defn
async def save_personalized_content_activity(input_params: SaveContentInput) -> bool:
    """
    Save personalized content to the database.
    
    Args:
        input_params: SaveContentInput containing:
            - company_info_id: ID of the company info
            - target_account_id: ID of the target account
            - original_text: Original text
            - personalized_text: Personalized text
            - text_type: Type of text
        
    Returns:
        Boolean indicating success
    """
    activity.logger.info(f"Saving personalized content for company {input_params.company_info_id}, target {input_params.target_account_id}")
    
    try:
        with _get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Insert personalized content
                cursor.execute(
                    """
                    INSERT INTO personalized_content
                    (company_info_id, target_account_id, original_text, personalized_text, text_type)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (input_params.company_info_id, input_params.target_account_id,
                     input_params.original_text, input_params.personalized_text, input_params.text_type)
                )
                result = cursor.fetchone()
                conn.commit()
                
                activity.logger.info(f"Saved personalized content with ID: {result[0]}")
                return True
    
    except Exception as e:
        activity.logger.error(f"Error saving personalized content: {str(e)}")
        raise