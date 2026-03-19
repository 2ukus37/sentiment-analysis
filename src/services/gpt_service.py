"""
GPT Service: Enhanced cyberbullying detection using OpenAI GPT models via OpenRouter.
Provides context-aware analysis and reasoning capabilities.
"""
import logging
from typing import Dict, Optional
from openai import OpenAI
import os


class GPTService:
    """
    Service for GPT-enhanced cyberbullying detection.
    Uses OpenRouter API for access to various models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GPT service.
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
        """
        self.logger = logging.getLogger(__name__)
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            self.logger.warning("No OpenRouter API key provided. GPT features will be disabled.")
            self.enabled = False
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key
                )
                self.enabled = True
                self.logger.info("GPT service initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize GPT service: {e}")
                self.enabled = False
                self.client = None
        
        # Model configuration
        self.model = "openai/gpt-3.5-turbo"  # Fast and cost-effective
        # Alternative: "openai/gpt-4" for better accuracy
    
    def analyze_text(self, text: str, context: Optional[str] = None) -> Dict:
        """
        Analyze text for cyberbullying using GPT.
        
        Args:
            text: Text to analyze
            context: Optional context about the text source
            
        Returns:
            Dictionary with GPT analysis results
        """
        if not self.enabled:
            return {
                'enabled': False,
                'error': 'GPT service not available'
            }
        
        try:
            # Construct prompt
            system_prompt = """You are an expert at detecting cyberbullying, hate speech, and personal attacks in online text.

Analyze the given text and determine:
1. Is it cyberbullying/hate speech/personal attack? (yes/no)
2. Severity level (low/medium/high)
3. Type (hate speech, personal attack, harassment, threat, none)
4. Reasoning for your decision
5. Confidence score (0-100)

Respond in JSON format:
{
    "is_cyberbullying": true/false,
    "severity": "low/medium/high/none",
    "type": "hate_speech/personal_attack/harassment/threat/none",
    "reasoning": "explanation",
    "confidence": 85
}"""
            
            user_prompt = f"Analyze this text: \"{text}\""
            if context:
                user_prompt += f"\n\nContext: {context}"
            
            # Call GPT API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=300
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, extract key information
                result = {
                    'is_cyberbullying': 'yes' in content.lower() or 'true' in content.lower(),
                    'severity': 'unknown',
                    'type': 'unknown',
                    'reasoning': content,
                    'confidence': 50
                }
            
            result['enabled'] = True
            result['model'] = self.model
            
            self.logger.info(f"GPT analysis: {result['is_cyberbullying']} (confidence: {result.get('confidence', 0)}%)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"GPT analysis error: {e}")
            return {
                'enabled': True,
                'error': str(e)
            }
    
    def get_detailed_analysis(self, text: str) -> Dict:
        """
        Get detailed analysis with reasoning.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detailed analysis with reasoning steps
        """
        if not self.enabled:
            return {
                'enabled': False,
                'error': 'GPT service not available'
            }
        
        try:
            prompt = f"""Analyze this text for cyberbullying and provide detailed reasoning:

Text: "{text}"

Provide:
1. Initial assessment
2. Key indicators found
3. Context analysis
4. Final verdict with confidence
5. Recommendations"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return {
                'enabled': True,
                'analysis': response.choices[0].message.content,
                'model': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Detailed analysis error: {e}")
            return {
                'enabled': True,
                'error': str(e)
            }
