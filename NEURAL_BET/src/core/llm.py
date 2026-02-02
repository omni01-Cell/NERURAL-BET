# -*- coding: utf-8 -*-
import os
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMFactory:
    """
    Factory to create LLM instances based on the requested provider and model.
    Updated Standards 2026: Mistral, Groq & Fireworks (Kimi).
    """

    @staticmethod
    def get_mistral_model(model_name: str = "mistral-small-latest", temperature: float = 0.0):
        """
        Returns a Mistral AI model instance.
        """
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is missing in .env")
            
        return ChatMistralAI(
            model=model_name,
            temperature=temperature,
            mistral_api_key=api_key
        )

    @staticmethod
    def get_groq_model(model_name: str = "groq/compound", temperature: float = 0.0):
        """
        Returns a Groq model instance.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing in .env")
            
        return ChatGroq(
            model_name=model_name,
            temperature=temperature,
            groq_api_key=api_key
        )
    
    @staticmethod
    def get_fireworks_model(model_name: str = "accounts/fireworks/models/kimi-k2p5", temperature: float = 0.6):
        """
        Returns a Fireworks AI model instance (via OpenAI compatible interface).
        Targeting Kimi k2.5 for high-level reasoning.
        """
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            raise ValueError("FIREWORKS_API_KEY is missing in .env")

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1/chat/completions" # Base URL for OpenAI compat
        )

    @staticmethod
    def create(agent_role: str):
        """
        Centralized mapping of Agent Role to Model Selection (2026 Strategy).
        """
        if agent_role == "metrician":
            # Mistral Small: Fast & Cost Efficient for stats
            return LLMFactory.get_mistral_model("mistral-small-latest", temperature=0.1)
        
        elif agent_role == "tactician":
            # Mistral Large: High intelligence for tactical analysis
            return LLMFactory.get_mistral_model("mistral-large-latest", temperature=0.2)
        
        elif agent_role == "psych":
             # Mistral Small is sufficient for sentiment/news
             return LLMFactory.get_mistral_model("mistral-small-latest", temperature=0.3)
        
        elif agent_role == "devils_advocate":
            # Groq Compound -> Excellent for critical/contrarian tasks
            return LLMFactory.get_groq_model("groq/compound", temperature=0.7)
        
        elif agent_role == "value_hunter":
             # Groq Compound -> Cold logic, high speed
             return LLMFactory.get_groq_model("groq/compound", temperature=0.0)

        elif agent_role == "orchestrator":
             # Kimi k2.5 via Fireworks -> The "Thinking" Model replacement
             return LLMFactory.get_fireworks_model("accounts/fireworks/models/kimi-k2p5", temperature=0.6)
             
        elif agent_role == "x_factor":
            return LLMFactory.get_groq_model("groq/compound", temperature=0.4)
            
        else:
            # Fallback
            return LLMFactory.get_mistral_model("mistral-small-latest")
