from typing import List

def generate_disease_search_terms(disease_name: str, disease_name_en: str = None) -> List[str]:
    """疾患に関する効果的な検索語を生成する"""
    search_terms = []
    
    # 基本検索語
    if disease_name:
        # 日本語の検索語
        ja_suffixes = [
            '患者会', '患者の会', '友の会',
            '家族会', '支援団体', '支援グループ',
            '協会', 'サポート', '相談窓口'
        ]
        
        for suffix in ja_suffixes:
            search_terms.append(f"{disease_name} {suffix}")
    
    # 英語名がある場合
    if disease_name_en:
        en_suffixes = [
            'patient association', 'support group',
            'foundation', 'society', 'patients',
            'community', 'organization'
        ]
        
        for suffix in en_suffixes:
            search_terms.append(f"{disease_name_en} {suffix}")
    
    return search_terms
