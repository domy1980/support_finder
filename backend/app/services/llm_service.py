#backend/app/services/llm_service.py

import json
from typing import Dict, Any, List
from app.llm.providers.lm_studio import LMStudioProvider

class LLMService:
    def __init__(self):
        self.provider = LMStudioProvider()
    
    async def extract_organization_info(self, text: str, disease_name: str) -> Dict[str, Any]:
        prompt = f"""
        以下のテキストから、「{disease_name}」に関連する患者会や支援団体の情報を抽出してください。
        
        テキスト：
        {text[:3000]}
        
        以下の形式でJSONを返してください：
        {{
            "organizations": [
                {{
                    "name": "団体名",
                    "url": "ウェブサイトURL",
                    "description": "簡単な説明",
                    "contact": "連絡先情報",
                    "type": "patient/family/support"
                }}
            ]
        }}
        """
        
        try:
            result = await self.provider.generate(prompt, temperature=0.3)
            content = result["content"]
            
            # JSONを抽出
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"organizations": []}
        except Exception as e:
            return {"organizations": []}
    
    async def check_health(self) -> bool:
        return await self.provider.health_check()
    
    async def get_available_models(self) -> List[str]:
        return await self.provider.get_available_models()
