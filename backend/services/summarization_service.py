import os
from openai import OpenAI
import asyncio
from typing import List, Dict


class SummarizationService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)
    
    async def summarize_segments(self, segments: List[Dict], keyword: str) -> str:
        """Summarize transcript segments using GPT-3.5-turbo or GPT-4o-mini"""
        if not segments:
            return "No relevant segments found for summarization."
        
        # Combine segment texts
        segment_texts = "\n".join([
            f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}"
            for seg in segments
        ])
        
        # Limit input to avoid excessive tokens (keep first 2000 chars)
        if len(segment_texts) > 2000:
            segment_texts = segment_texts[:2000] + "..."
        
        system_prompt = """You are a concise summarization assistant. Summarize only the transcript segments where the keyword appears. Be concise and meaningful. Avoid redundancies. Return 2-3 small paragraphs maximum."""
        
        user_prompt = f"""Summarize the following transcript segments where the keyword "{keyword}" appears:

{segment_texts}

Provide a concise summary in 2-3 short paragraphs."""
        
        def summarize():
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using GPT-3.5-turbo for cost efficiency
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,  # Limit tokens for cost control
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(None, summarize)
        
        return summary

