"""
Vision and Voice Integration - Handles screen capture, vision analysis, and voice transcription.
Integrates with Whisper API for speech-to-text and OpenAI Vision for image analysis.
"""

import asyncio
import base64
import logging
import io
from typing import Optional, Dict, Any
from pathlib import Path

import aiohttp
from PIL import Image, ImageGrab

from backend.config import settings

logger = logging.getLogger(__name__)


class VisionVoiceManager:
    """
    Manages vision and voice capabilities for the agent.
    Provides screen capture, image analysis, and voice transcription.
    """
    
    def __init__(self):
        """Initialize Vision and Voice Manager."""
        self.whisper_model = settings.WHISPER_MODEL
        self.audio_sample_rate = settings.AUDIO_SAMPLE_RATE
        self.max_audio_duration = settings.MAX_AUDIO_DURATION
        
        logger.info("Vision and Voice Manager initialized")
    
    async def capture_screen(
        self,
        region: Optional[tuple] = None,
    ) -> str:
        """
        Capture the screen and return as base64 image.
        
        Args:
            region: Optional tuple of (left, top, right, bottom) for partial capture
        
        Returns:
            Base64 encoded image string
        """
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info("Screen captured successfully")
            return img_base64
        
        except Exception as e:
            logger.error(f"Error capturing screen: {str(e)}")
            raise
    
    async def analyze_image(
        self,
        image_path_or_base64: str,
        query: str,
    ) -> str:
        """
        Analyze an image using vision capabilities.
        
        Args:
            image_path_or_base64: Path to image or base64 encoded image
            query: Question or task related to the image
        
        Returns:
            Analysis result
        """
        try:
            # Convert image to base64 if it's a file path
            if image_path_or_base64.startswith("/") or image_path_or_base64.startswith("."):
                with open(image_path_or_base64, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode()
            else:
                image_base64 = image_path_or_base64
            
            # TODO: Integrate with OpenAI Vision API or similar
            # For now, return a placeholder
            logger.info(f"Image analysis requested: {query}")
            return "Image analysis not yet implemented"
        
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise
    
    async def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio file to text using Whisper API.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es')
        
        Returns:
            Transcribed text
        """
        try:
            # Check file exists
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # TODO: Integrate with Whisper API
            # For now, return a placeholder
            logger.info(f"Audio transcription requested for: {audio_path}")
            return "Audio transcription not yet implemented"
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    async def describe_screen(self) -> str:
        """
        Capture and describe the current screen.
        
        Returns:
            Description of the screen
        """
        try:
            # Capture screen
            screenshot_base64 = await self.capture_screen()
            
            # Analyze the screenshot
            description = await self.analyze_image(
                screenshot_base64,
                "Describe what you see on this screen in detail.",
            )
            
            return description
        
        except Exception as e:
            logger.error(f"Error describing screen: {str(e)}")
            raise
    
    async def find_element_on_screen(
        self,
        element_description: str,
    ) -> Optional[Dict[str, int]]:
        """
        Find an element on screen by description.
        
        Args:
            element_description: Description of the element to find
        
        Returns:
            Coordinates (x, y) or None if not found
        """
        try:
            # Capture screen
            screenshot_base64 = await self.capture_screen()
            
            # Ask vision to find the element
            response = await self.analyze_image(
                screenshot_base64,
                f"Find and locate the following element on screen: {element_description}. "
                f"Return the approximate center coordinates (x, y) relative to the screen.",
            )
            
            # TODO: Parse response to extract coordinates
            logger.info(f"Element search result: {response}")
            return None
        
        except Exception as e:
            logger.error(f"Error finding element: {str(e)}")
            raise
    
    async def get_screen_state(self) -> Dict[str, Any]:
        """
        Get the current state of the screen.
        
        Returns:
            Dictionary with screen information
        """
        try:
            screenshot = ImageGrab.grab()
            
            return {
                "width": screenshot.width,
                "height": screenshot.height,
                "format": "RGB",
                "screenshot_base64": base64.b64encode(
                    io.BytesIO(screenshot.tobytes()).getvalue()
                ).decode(),
            }
        
        except Exception as e:
            logger.error(f"Error getting screen state: {str(e)}")
            raise


# Global vision/voice manager instance
vision_voice_manager = VisionVoiceManager()
