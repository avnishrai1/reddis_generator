import os
from groq import Groq
from anthropic import Anthropic
import json

class LLMService:
    def __init__(self, api_key, provider='groq'):
        self.provider = provider
        if provider == 'groq':
            self.client = Groq(api_key=api_key)
            self.model = 'llama-3.3-70b-versatile'
        else :
            print("Dosent import any model check your LLM")
    
    def generate_posts(self, user_input, feedback=None, selected_post=None):
        
        
        if feedback and selected_post:
            prompt = f"""You are a Reddit post generator. Based on the original idea and user feedback, generate 5 improved Reddit posts.

Original idea: {user_input}
Previous post: {selected_post.get('title', '')} - {selected_post.get('content', '')}
User feedback: {feedback}

Generate 5 diverse Reddit posts that incorporate this feedback. Each post should be engaging, conversational, and authentic.

Return ONLY a valid JSON array with 5 objects, each having "title" and "content" fields.
Format: [{{"title": "...", "content": "..."}}, ...]
Do not include markdown formatting or explanations."""
        else:
            prompt = f"""You are a Reddit post generator. Generate 5 diverse, engaging Reddit posts based on this idea: "{user_input}"

Each post should have:
- A compelling, clickable title
- Authentic, conversational content that feels natural on Reddit
- Appropriate length (150-300 words)
- Different styles/approaches to the same core idea

Return ONLY a valid JSON array with 5 objects, each having "title" and "content" fields.
Format: [{{"title": "...", "content": "..."}}, ...]
Do not include markdown formatting or explanations."""
        
        try:
            if self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a Reddit post generation expert. Always return valid JSON arrays only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.9,
                    max_tokens=2000,
                )
                content = response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1.0
                )
                content = response.content[0].text
            
            # Clean and parse response
            content = content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            # Extract JSON array
            import re
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                content = json_match.group(0)
            
            posts = json.loads(content)
            
            # Validate format
            if not isinstance(posts, list):
                raise ValueError("Response is not a list")
            
            # Ensure exactly 5 posts
            posts = posts[:5]
            while len(posts) < 5:
                posts.append({
                    "title": f"Post Variant {len(posts) + 1}",
                    "content": "Generated post content here."
                })
            
            return posts
            
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            raise Exception(f"Failed to generate posts: {str(e)}")