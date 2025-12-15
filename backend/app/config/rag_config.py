"""
Centralized RAG (Retrieval-Augmented Generation) Configuration

This module manages all AI model configurations for the application,
including LLM settings, embedding models, and prompt templates.
"""

from app.config.settings import settings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Optional


class RAGConfig:
    """Centralized configuration for RAG pipeline"""

    # Model Configuration (from environment)
    GOOGLE_API_KEY = settings.GOOGLE_API_KEY
    MODEL_NAME = settings.GEMINI_MODEL
    EMBEDDING_MODEL = settings.GEMINI_EMBEDDING_MODEL
    TEMPERATURE = settings.GEMINI_TEMPERATURE
    MAX_OUTPUT_TOKENS = settings.GEMINI_MAX_OUTPUT_TOKENS

    # Text Splitting Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Vector Search Configuration
    TOP_K_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.7

    # RAG Prompt Templates
    SUMMARIZER_SYSTEM_PROMPT = """You are an expert at summarizing educational content.
Create a clear, concise, and comprehensive summary that captures the key points and main ideas.
Focus on the most important information that would help a student understand the material.
Keep the summary well-structured and easy to understand."""

    QUESTION_GENERATOR_SYSTEM_PROMPT = """You are an expert educator who creates engaging quiz questions.
Generate clear, well-structured questions that test understanding of the material.
For each question, provide:
1. The question text
2. Multiple choice options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format the output as JSON array with this structure:
[
  {
    "question": "Question text?",
    "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
    "correct_answer": "A",
    "explanation": "Explanation of the answer"
  }
]"""

    EXPLAINER_SYSTEM_PROMPT = """You are a helpful educational assistant who explains concepts clearly and comprehensively.
When provided with context, use it to give more accurate and relevant explanations.
Break down complex topics into understandable parts and provide examples where helpful.
Use the retrieved context to enhance your explanations and make them more specific to the user's learning materials."""

    RESOURCE_RECOMMENDER_SYSTEM_PROMPT = """You are an expert at recommending educational resources.
Based on the topic or content provided, suggest relevant learning resources including:
- Articles and tutorials
- Video courses and lectures
- Books and textbooks
- Online courses

Format the output as JSON array:
[
  {
    "title": "Resource title",
    "description": "Brief description",
    "url": "URL or search suggestion",
    "type": "article|video|book|course",
    "relevance_score": 0.0-1.0
  }
]"""

    @classmethod
    def get_llm(cls, temperature: Optional[float] = None) -> ChatGoogleGenerativeAI:
        """
        Get configured Gemini LLM instance
        
        Args:
            temperature: Optional temperature override
        
        Returns:
            ChatGoogleGenerativeAI instance
        """
        return ChatGoogleGenerativeAI(
            model=cls.MODEL_NAME,
            google_api_key=cls.GOOGLE_API_KEY,
            temperature=temperature if temperature is not None else cls.TEMPERATURE,
            max_output_tokens=cls.MAX_OUTPUT_TOKENS,
            convert_system_message_to_human=True  # Gemini compatibility
        )

    @classmethod
    def get_embeddings(cls) -> GoogleGenerativeAIEmbeddings:
        """
        Get configured Gemini embeddings instance
        
        Returns:
            GoogleGenerativeAIEmbeddings instance
        """
        return GoogleGenerativeAIEmbeddings(
            model=cls.EMBEDDING_MODEL,
            google_api_key=cls.GOOGLE_API_KEY
        )

    @classmethod
    def get_text_splitter(cls) -> RecursiveCharacterTextSplitter:
        """
        Get configured text splitter for chunking documents
        
        Returns:
            RecursiveCharacterTextSplitter instance
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=cls.CHUNK_SIZE,
            chunk_overlap=cls.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )


# Singleton instances for reuse
rag_config = RAGConfig()
