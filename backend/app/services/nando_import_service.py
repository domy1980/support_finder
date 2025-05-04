from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session
from app.models.disease import Disease
from app.schemas.disease import DiseaseCreate
import re
import uuid

class NandoImportService:
    def __init__(self):
        pass

    def import_nando_data(self, db: Session, file_path: str) -> Dict[str, Any]:
        """NANDOデータファイルをインポート"""
        try:
            # Excelファイルを読み込む
            df = pd.read_excel(file_path, header=0)
            
            # 必要なカラムが存在するか確認
            required_columns = ['NANDO', 'label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "status": "error",
                    "message": f"必要なカラムが見つかりません: {', '.join(missing_columns)}",
                    "imported": 0
                }
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            # データをインポート
            for index, row in df.iterrows():
                try:
                    nando_id = str(row['NANDO']).strip() if pd.notna(row['NANDO']) else None
                    disease_name = str(row['label']).strip() if pd.notna(row['label']) else None
                    
                    if not disease_name:
                        skipped_count += 1
                        continue
                    
                    # 病名が英語かどうかを判定
                    is_english = not re.search(r'[ぁ-んァ-ン一-龥]', disease_name)
                    
                    # UUIDを生成
                    disease_id = str(uuid.uuid4())
                    
                    # 既存のデータを確認
                    existing_disease = None
                    if nando_id:
                        existing_disease = db.query(Disease).filter(Disease.nando_id == nando_id).first()
                    else:
                        # NANDOがない場合は名前で検索
                        existing_disease = db.query(Disease).filter(Disease.name == disease_name).first()
                    
                    if existing_disease:
                        # 既存のデータを更新
                        existing_disease.name = disease_name
                        if is_english:
                            existing_disease.name_en = disease_name
                    else:
                        # 新規データを作成
                        db_disease = Disease(
                            id=disease_id,
                            nando_id=nando_id,
                            name=disease_name,
                            name_en=disease_name if is_english else None,
                            is_designated_intractable=False,
                            is_chronic_childhood=False,
                            is_searchable=False  # デフォルトは検索対象外
                        )
                        db.add(db_disease)
                        imported_count += 1
                    
                except Exception as e:
                    errors.append(f"行 {index + 2}: {str(e)}")
                    continue
            
            # コミット
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                return {
                    "status": "error",
                    "message": f"データベースエラー: {str(e)}",
                    "imported": 0
                }
            
            return {
                "status": "success",
                "message": f"{imported_count}件のデータをインポートしました。{skipped_count}件スキップしました。",
                "imported": imported_count,
                "skipped": skipped_count,
                "errors": errors if errors else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"ファイル読み込みエラー: {str(e)}",
                "imported": 0
            }
    
    def get_disease_hierarchy(self, db: Session) -> Dict[str, Any]:
        """疾患の階層構造を取得"""
        diseases = db.query(Disease).all()
        
        hierarchy = {}
        for disease in diseases:
            if disease.parent_disease_id:
                if disease.parent_disease_id not in hierarchy:
                    hierarchy[disease.parent_disease_id] = []
                hierarchy[disease.parent_disease_id].append(disease)
        
        return hierarchy
