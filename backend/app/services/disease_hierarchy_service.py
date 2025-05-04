from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session
from app.models.disease import Disease
import json
import re

class DiseaseHierarchyService:
    def __init__(self):
        # 検索から除外する大分類のキーワード
        self.excluded_categories = {
            '遺伝検査用疾患群',
            '指定難病',
            '神経・筋疾患',
            '代謝系疾患',
            '皮膚・結合組織疾患',
            '免疫系疾患',
            '循環器系疾患',
            '血液系疾患',
            '腎・泌尿器系疾患',
            '骨・関節系疾患',
            '内分泌系疾患',
            '呼吸器系疾患',
            '視覚系疾患',
            '聴覚・平衡機能系疾患',
            '消化器系疾患',
            '染色体または遺伝子に変化を伴う症候群',
            '耳鼻科系疾患',
            '難病',
            '小児慢性特定疾病'
        }
        
        # サブタイプを示すパターン
        self.subtype_patterns = [
            r'^.+[IⅠ1一][型]?$',  # I型、1型、一型
            r'^.+[IIⅡ2二][型]?$',  # II型、2型、二型
            r'^.+[IIIⅢ3三][型]?$',  # III型、3型、三型
            r'^.+[IVⅣ4四][型]?$',  # IV型、4型、四型
            r'^.+[VⅤ5五][型]?$',  # V型、5型、五型
            r'^.+タイプ[1-9]$',  # タイプ1など
            r'^.+[型][A-Z]$',  # 型A、型Bなど
            r'脱髄型.+$',
            r'軸索型.+$',
            r'中間型.+$',
            r'^.+早期発症型$',
            r'^.+遅発型$',
            r'^.+先天性$',
            r'^.+後天性$',
            r'^.+家族性$',
            r'^.+孤発性$',
            r'^.+急性$',
            r'^.+慢性$',
            r'^.+重症型$',
            r'^.+軽症型$'
        ]
        
        # NANDOのIDパターンによるサブタイプ判定
        self.subtype_id_patterns = [
            r'NANDO:\d+\.\d+',  # 小数点を含むID（例：NANDO:1200001.1）
        ]
    
    def get_searchable_diseases(self, db: Session) -> List[Disease]:
        """検索すべき疾患のリストを取得"""
        all_diseases = db.query(Disease).all()
        
        # 階層構造を構築
        parent_child_map = {}  # parent_id -> [child_diseases]
        disease_map = {}  # nando_id -> disease
        
        for disease in all_diseases:
            disease_map[disease.nando_id] = disease
            
            if disease.parent_disease_id and disease.parent_disease_id != 'owl:Thing':
                if disease.parent_disease_id not in parent_child_map:
                    parent_child_map[disease.parent_disease_id] = []
                parent_child_map[disease.parent_disease_id].append(disease)
        
        # 検索対象の疾患を選定
        searchable_diseases = []
        excluded_nando_ids = set()
        
        for disease in all_diseases:
            # 除外カテゴリーに該当する場合はスキップ
            if disease.name in self.excluded_categories:
                excluded_nando_ids.add(disease.nando_id)
                continue
            
            # 親が除外カテゴリーの場合もスキップ
            if disease.parent_disease_id in excluded_nando_ids:
                excluded_nando_ids.add(disease.nando_id)
                continue
            
            # サブタイプの場合は親疾患を優先
            if self._is_subtype(disease):
                continue
            
            # 子疾患がある場合、子がすべてサブタイプかチェック
            children = parent_child_map.get(disease.nando_id, [])
            all_children_are_subtypes = all(
                self._is_subtype(child) for child in children
            )
            
            # 子がすべてサブタイプの場合、この疾患を検索対象に
            if children and all_children_are_subtypes:
                searchable_diseases.append(disease)
            # 子がない場合、この疾患を検索対象に
            elif not children:
                searchable_diseases.append(disease)
        
        return searchable_diseases
    
    def _is_subtype(self, disease: Disease) -> bool:
        """疾患がサブタイプかどうかを判定"""
        # 疾患名でパターンマッチング
        for pattern in self.subtype_patterns:
            if re.search(pattern, disease.name):
                return True
        
        # NANDO IDでパターンマッチング
        if disease.nando_id:
            for pattern in self.subtype_id_patterns:
                if re.search(pattern, disease.nando_id):
                    return True
        
        # 親疾患との名前の類似性をチェック
        if disease.parent_disease_id and disease.parent_disease_id != 'owl:Thing':
            parent = self._get_parent_disease(disease.parent_disease_id)
            if parent and self._is_name_variant(disease.name, parent.name):
                return True
        
        return False
    
    def _is_name_variant(self, child_name: str, parent_name: str) -> bool:
        """子疾患名が親疾患名のバリエーションかどうかを判定"""
        # 親疾患名が子疾患名に含まれ、かつ追加の修飾語がある場合
        if parent_name in child_name and len(child_name) > len(parent_name):
            return True
        return False
    
    def _get_parent_disease(self, parent_id: str) -> Optional[Disease]:
        """親疾患を取得（簡易版）"""
        # 実際の実装では、セッションを使用してデータベースから取得
        return None
    
    def get_disease_hierarchy_info(self, db: Session, disease_id: str) -> Dict:
        """疾患の階層情報を取得"""
        disease = db.query(Disease).filter(Disease.id == disease_id).first()
        if not disease:
            return None
        
        # 親疾患を取得
        parent = None
        if disease.parent_disease_id and disease.parent_disease_id != 'owl:Thing':
            parent = db.query(Disease).filter(Disease.nando_id == disease.parent_disease_id).first()
        
        # 子疾患を取得
        children = db.query(Disease).filter(Disease.parent_disease_id == disease.nando_id).all()
        
        return {
            'disease': {
                'id': disease.id,
                'name': disease.name,
                'nando_id': disease.nando_id
            },
            'parent': {
                'id': parent.id,
                'name': parent.name,
                'nando_id': parent.nando_id
            } if parent else None,
            'children': [
                {
                    'id': child.id,
                    'name': child.name,
                    'nando_id': child.nando_id
                } for child in children
            ]
        }
    
    def get_disease_hierarchy_stats(self, db: Session) -> Dict:
        """疾患階層の統計情報を取得"""
        all_diseases = db.query(Disease).all()
        searchable_diseases = self.get_searchable_diseases(db)
        
        # サブタイプの統計
        subtypes = [d for d in all_diseases if self._is_subtype(d)]
        
        return {
            'total_diseases': len(all_diseases),
            'searchable_diseases': len(searchable_diseases),
            'excluded_categories': list(self.excluded_categories),
            'reduction_rate': f"{(1 - len(searchable_diseases) / len(all_diseases)) * 100:.1f}%",
            'subtypes_count': len(subtypes),
            'subtypes_patterns': len(self.subtype_patterns)
        }
