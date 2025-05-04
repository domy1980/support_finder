from abc import ABC, abstractmethod
from typing import Dict, Any, List

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        pass
