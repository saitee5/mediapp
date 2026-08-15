import os
from typing import Optional, Any
from src.utils.config import settings
from src.utils.logger import logger

class LLMClientManager:
    """Manages LLM client instances for LangGraph structured output pipelines."""
    _instance: Optional[Any] = None
    _chat_instances: dict = {}

    @classmethod
    def get_pipeline_llm(
        cls,
        model_name: Optional[str] = None,
        temperature: float = 0.0,
    ):
        """
        Returns a Chat model configured for structured output.
        Prioritizes ChatVertexAI (as in main_pipeline_demo.ipynb), with
        graceful fallback to ChatGoogleGenerativeAI or ChatGroq.
        """
        model = model_name or settings.DEFAULT_LLM_MODEL
        key = f"{model}:{temperature}"
        if key in cls._chat_instances:
            return cls._chat_instances[key]

        # 1. Try ChatVertexAI (preferred in notebook)
        try:
            from langchain_google_vertexai import ChatVertexAI
            llm = ChatVertexAI(
                model=model,
                temperature=temperature,
                location=settings.DEFAULT_VERTEX_LOCATION,
            )
            logger.info(f"Initialized ChatVertexAI LLM model={model} location={settings.DEFAULT_VERTEX_LOCATION}")
            cls._chat_instances[key] = llm
            return llm
        except Exception as vertex_err:
            logger.warning(f"ChatVertexAI initialization warning: {vertex_err}")

        # 2. Try ChatGoogleGenerativeAI with API Key
        google_key = settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        if google_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model=model if "gemini" in model else "gemini-2.5-flash",
                    temperature=temperature,
                    google_api_key=google_key,
                )
                logger.info(f"Initialized ChatGoogleGenerativeAI LLM with API key.")
                cls._chat_instances[key] = llm
                return llm
            except Exception as genai_err:
                logger.warning(f"ChatGoogleGenerativeAI initialization warning: {genai_err}")

        # 3. Fallback to ChatGroq if GROQ_API_KEY is available
        if settings.GROQ_API_KEY:
            try:
                from langchain_groq import ChatGroq
                groq_model = "llama-3.3-70b-versatile" if "gemini" in model else model
                llm = ChatGroq(
                    model=groq_model,
                    temperature=temperature,
                    groq_api_key=settings.GROQ_API_KEY,
                )
                logger.info(f"Initialized ChatGroq fallback LLM model={groq_model}.")
                cls._chat_instances[key] = llm
                return llm
            except Exception as groq_err:
                logger.warning(f"ChatGroq initialization warning: {groq_err}")

        # Default fallback to ChatVertexAI
        from langchain_google_vertexai import ChatVertexAI
        llm = ChatVertexAI(
            model=model,
            temperature=temperature,
            location=settings.DEFAULT_VERTEX_LOCATION,
        )
        cls._chat_instances[key] = llm
        return llm

    @classmethod
    def get_groq_client(cls):
        """Returns AsyncGroq instance for audio/whisper transcription if needed."""
        if cls._instance is None and settings.GROQ_API_KEY:
            try:
                from groq import AsyncGroq
                cls._instance = AsyncGroq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.warning(f"AsyncGroq client initialization warning: {e}")
        return cls._instance

def get_pipeline_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
):
    """Convenience function to get the shared LLM instance."""
    return LLMClientManager.get_pipeline_llm(model_name=model_name, temperature=temperature)

def get_chat_groq(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
):
    """Compatibility alias for get_pipeline_llm."""
    return LLMClientManager.get_pipeline_llm(model_name=model_name, temperature=temperature)

def get_groq_client():
    """Convenience function to get the shared AsyncGroq client."""
    return LLMClientManager.get_groq_client()


