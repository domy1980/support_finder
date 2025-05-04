import aiohttp
from typing import Dict, Any, List
from app.config import settings
from app.llm.providers.base import LLMProvider

class LMStudioProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.LM_STUDIO_BASE_URL
        self.model = settings.LM_STUDIO_MODEL
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
            }
            
            try:
                async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "content": result["choices"][0]["message"]["content"],
                            "usage": result.get("usage", {}),
                            "model": result.get("model", self.model)
                        }
                    else:
                        raise Exception(f"LM Studio error: {response.status}")
            except Exception as e:
                raise Exception(f"Failed to connect to LM Studio: {str(e)}")
    
    async def count_tokens(self, text: str) -> int:
        return len(text.split()) + len(text) // 4
    
    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/models") as response:
                    return response.status == 200
        except:
            return False
    
    async def get_available_models(self) -> List[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/models") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["id"] for model in data.get("data", [])]
                    return []
        except:
            return []
