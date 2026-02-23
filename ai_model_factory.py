"""
AI Vision Model Factory
Provides callable vision model classes for screen analysis.
Supports Anthropic (default) and Google Gemini backends.

Usage:
    from ai_model_factory import get_vision_model
    model = get_vision_model()            # Anthropic (default)
    model = get_vision_model("gemini")    # Google Gemini
    response = model(image_bytes, "Analyze this screenshot")
"""

import os
import base64
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class BaseVisionModel(ABC):
    """Abstract base class for vision models. All models are callable."""

    @abstractmethod
    def __call__(self, image_bytes: bytes, prompt: str) -> str:
        """
        Analyze an image with a text prompt.

        Args:
            image_bytes: Raw image bytes (PNG/JPEG).
            prompt: Text prompt describing what to analyze.

        Returns:
            The model's text response.
        """
        ...


class AnthropicVisionModel(BaseVisionModel):
    """Anthropic Claude vision model (default)."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Set it in your .env file or environment variables."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def __call__(self, image_bytes: bytes, prompt: str) -> str:
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )
        return message.content[0].text


class GeminiVisionModel(BaseVisionModel):
    """Google Gemini vision model (alternative)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Set it in your .env file or environment variables."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def __call__(self, image_bytes: bytes, prompt: str) -> str:
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(image_bytes))
        response = self.model.generate_content([prompt, image])
        return response.text


# ── Factory ──────────────────────────────────────────────────────────── #

_PROVIDERS = {
    "anthropic": AnthropicVisionModel,
    "gemini": GeminiVisionModel,
}


def get_vision_model(provider: str = "anthropic", **kwargs) -> BaseVisionModel:
    """
    Factory function that returns a callable vision model instance.

    Args:
        provider: "anthropic" (default) or "gemini".
        **kwargs: Extra keyword arguments forwarded to the model constructor
                  (e.g. model="claude-sonnet-4-20250514").

    Returns:
        A callable BaseVisionModel instance.
    """
    provider = provider.lower().strip()
    if provider not in _PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Available: {', '.join(_PROVIDERS.keys())}"
        )
    return _PROVIDERS[provider](**kwargs)
