import os
import requests
from typing import List, Dict, Any, Optional
import openai
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Handles interactions with LLM APIs (OpenAI and Perplexity)"""
    
    def __init__(self, openai_api_key: Optional[str] = None, perplexity_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.perplexity_api_key = perplexity_api_key
        
        # Only initialize OpenAI client if we have a valid API key
        if openai_api_key and openai_api_key != "your-openai-api-key":
            openai.api_key = openai_api_key
            self.client = openai.OpenAI(api_key=openai_api_key)
        else:
            self.client = None
        
        # Perplexity API setup
        self.perplexity_headers = {
            "Authorization": f"Bearer {perplexity_api_key}" if perplexity_api_key else "",
            "Content-Type": "application/json"
        }
    
    def generate_response_with_context(
        self, 
        query: str, 
        context: List[Dict[str, Any]], 
        model: str = "perplexity"
    ) -> str:
        """Generate response using LLM with retrieved context"""
        try:
            # Prepare context
            context_text = "\n\n".join([doc["text"] for doc in context])
            
            # Create system prompt
            system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
            Please answer the question using only the information provided in the context. 
            If the context doesn't contain enough information to answer the question, say so.
            Be concise and accurate in your responses."""
            
            # Create user prompt
            user_prompt = f"""Context: {context_text}

Question: {query}

Please provide a clear and accurate answer based on the context above."""
            
            # Try OpenAI first if available
            if self.client and self.openai_api_key and self.openai_api_key != "your-openai-api-key":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1
                )
                return response.choices[0].message.content.strip()
            
            # Fallback to Perplexity API
            elif self.perplexity_api_key and self.perplexity_api_key != "your-perplexity-api-key":
                perplexity_url = "https://api.perplexity.ai/chat/completions"
                payload = {
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
                
                response = requests.post(
                    perplexity_url,
                    headers=self.perplexity_headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
            
            else:
                raise ValueError("No LLM API keys provided")
            
        except Exception as e:
            logger.error(f"Error generating response with LLM: {e}")
            raise
    
    def generate_structured_response(
        self, 
        query: str, 
        context: List[Dict[str, Any]], 
        model: str = "perplexity"
    ) -> Dict[str, Any]:
        """Generate structured response with decision, amount, and justification"""
        try:
            # Prepare context
            context_text = "\n\n".join([doc["text"] for doc in context])
            
            # Create system prompt for structured response
            system_prompt = """You are an insurance policy analyzer. Based on the provided policy document context, 
            analyze the query and provide a structured response with:
            1. Decision: Whether the claim/request is approved or rejected
            2. Amount: The payout amount if applicable (or "N/A" if not applicable)
            3. Justification: Detailed explanation with specific policy clauses referenced
            
            Format your response as a JSON object with these fields."""
            
            # Create user prompt
            user_prompt = f"""Policy Context: {context_text}

Query: {query}

Please analyze this query against the policy and provide a structured response."""
            
            # Try OpenAI first if available
            if self.client and self.openai_api_key and self.openai_api_key != "your-openai-api-key":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.1
                )
                response_text = response.choices[0].message.content.strip()
            
            # Fallback to Perplexity API
            elif self.perplexity_api_key and self.perplexity_api_key != "your-perplexity-api-key":
                perplexity_url = "https://api.perplexity.ai/chat/completions"
                payload = {
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.1
                }
                
                response = requests.post(
                    perplexity_url,
                    headers=self.perplexity_headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
            
            else:
                raise ValueError("No LLM API keys provided")
            
            # Parse response (assuming it's JSON)
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # If JSON parsing fails, return structured text
            return {
                "decision": "Unable to parse structured response",
                "amount": "N/A",
                "justification": response_text
            }
            
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            raise
    
    def generate_simple_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate simple text response for general questions"""
        try:
            # Prepare context
            context_text = "\n\n".join([doc["text"] for doc in context])
            
            # Create prompt
            prompt = f"""Based on the following document context, answer the question:

Context: {context_text}

Question: {query}

Answer:"""
            
            # Try OpenAI first if available
            if self.client and self.openai_api_key and self.openai_api_key != "your-openai-api-key":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.1
                )
                return response.choices[0].message.content.strip()
            
            # Fallback to Perplexity API
            elif self.perplexity_api_key and self.perplexity_api_key != "your-perplexity-api-key":
                perplexity_url = "https://api.perplexity.ai/chat/completions"
                payload = {
                    "model": "sonar",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1
                }
                
                response = requests.post(
                    perplexity_url,
                    headers=self.perplexity_headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
            
            else:
                raise ValueError("No LLM API keys provided")
            
        except Exception as e:
            logger.error(f"Error generating simple response: {e}")
            raise 