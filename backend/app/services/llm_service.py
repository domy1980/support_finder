#backend/app/services/llm_service.py

import json
from typing import Dict, Any, List
from app.llm.providers.lm_studio import LMStudioProvider
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = LMStudioProvider()
    
    async def extract_organization_info(self, text: str, disease_name: str) -> Dict[str, Any]:
        """ウェブページから患者会・支援団体の情報を抽出"""
        logger.info(f"LLMに送信するテキストサイズ: {len(text)} 文字")
        
        # より詳細な指示を含むプロンプト
        prompt = f"""
あなたは医療支援団体情報の抽出スペシャリストです。以下のウェブページから「{disease_name}」に関連する患者会、家族会、支援団体などの情報を正確に抽出してください。

【ウェブページ内容】
{text[:4000]}

【抽出ルール】
1. 「{disease_name}」の患者や家族を支援する団体の情報を探してください
2. 製薬会社や営利企業、病院は対象外です（患者会・支援団体のみ）
3. 実際にテキスト内に明示されている情報のみを抽出してください。見つからなければ空の配列を返してください。
4. 抽出すべき情報:
   - 団体名: 組織の正式名称
   - URL: 団体のウェブサイト（URLがテキスト内に明示されている場合のみ）
   - 説明: 団体の目的や活動内容の簡単な説明
   - 連絡先: メール・電話番号・住所など
   - タイプ: "patient"(患者会)、"family"(家族会)、"support"(支援団体)のいずれか

【出力形式】
以下の形式のJSONを出力してください:
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

該当する団体が見つからない場合や、テンプレート値をそのまま使用せず、必ず空の配列を返してください: {{"organizations": []}}
テンプレートの値（"団体名"、"ウェブサイトURL"など）をそのまま返さないでください。
"""
        
        try:
            result = await self.provider.generate(prompt, temperature=0.3)
            content = result["content"]
            
            # JSONを抽出
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end]
                try:
                    parsed = json.loads(json_str)
                    
                    # テンプレート値のチェック
                    orgs = parsed.get("organizations", [])
                    filtered_orgs = []
                    
                    for org in orgs:
                        # テンプレート値かどうかチェック
                        if (org.get("name") == "団体名" or 
                            org.get("url") == "ウェブサイトURL" or 
                            org.get("description") == "簡単な説明"):
                            continue
                        
                        # 空の値を"不明"に置き換え
                        name = org.get("name", "")
                        if name and name != "":
                            filtered_orgs.append({
                                "name": name,
                                "url": org.get("url", "") if org.get("url", "") != "" else "不明",
                                "description": org.get("description", "") if org.get("description", "") != "" else "不明",
                                "contact": org.get("contact", "") if org.get("contact", "") != "" else "不明",
                                "type": org.get("type", "support")
                            })
                    
                    logger.info(f"フィルタリング後の組織数: {len(filtered_orgs)}")
                    return {"organizations": filtered_orgs}
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析エラー: {e}")
                    return {"organizations": []}
            else:
                logger.warning("JSONが見つかりませんでした")
                return {"organizations": []}
        except Exception as e:
            logger.error(f"LLMエラー: {e}")
            return {"organizations": []}
    
    async def check_health(self) -> bool:
        return await self.provider.health_check()
    
    async def get_available_models(self) -> List[str]:
        return await self.provider.get_available_models()
