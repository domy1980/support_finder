from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session
from app.models.disease import Disease
from app.schemas.disease import DiseaseCreate
import re
import uuid
import logging

logger = logging.getLogger(__name__)

class NandoImportService:
    def __init__(self):
        pass

    def import_nando_data(self, db: Session, file_path: str) -> Dict[str, Any]:
        """NANDOデータファイルをインポート"""
        try:
            # Excelファイルを読み込む
            logger.info(f"Importing NANDO data from {file_path}")
            try:
                df = pd.read_excel(file_path, header=0)
            except Exception as e:
                logger.error(f"Excel読み込みエラー: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Excel読み込みエラー: {str(e)}",
                    "imported": 0
                }
            
            # データフレームの情報をログに出力
            logger.info(f"DataFrame columns: {df.columns.tolist()}")
            logger.info(f"DataFrame shape: {df.shape}")
            logger.info(f"First few rows: {df.head().to_dict()}")
            
            # 必要なカラムが存在するか確認
            # 柔軟に対応するため、大文字小文字を区別せずに確認
            columns_lower = [col.lower() for col in df.columns]
            
            nando_col = None
            label_col = None
            
            # NANDO列を探す
            for col in df.columns:
                if col.lower() == 'nando' or 'nando' in col.lower():
                    nando_col = col
                    break
            
            # label列を探す
            for col in df.columns:
                if col.lower() == 'label' or 'label' in col.lower() or '名称' in col or '疾患名' in col:
                    label_col = col
                    break
            
            if not nando_col:
                logger.error("NANDO列が見つかりません")
                return {
                    "status": "error",
                    "message": "NANDO列が見つかりません。列名に'NANDO'を含む列が必要です。",
                    "imported": 0
                }
            
            if not label_col:
                logger.error("疾患名列が見つかりません")
                return {
                    "status": "error",
                    "message": "疾患名列が見つかりません。列名に'label'や'名称'、'疾患名'を含む列が必要です。",
                    "imported": 0
                }
            
            logger.info(f"Using columns: NANDO={nando_col}, label={label_col}")
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            # データをインポート
            for index, row in df.iterrows():
                try:
                    nando_id = str(row[nando_col]).strip() if pd.notna(row[nando_col]) else None
                    disease_name = str(row[label_col]).strip() if pd.notna(row[label_col]) else None
                    
                    if not disease_name:
                        logger.warning(f"行 {index + 2}: 疾患名が空のためスキップします")
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
                        logger.info(f"行 {index + 2}: 既存データを更新 - {disease_name}")
                        existing_disease.name = disease_name
                        if is_english:
                            existing_disease.name_en = disease_name
                    else:
                        # 新規データを作成
                        logger.info(f"行 {index + 2}: 新規データを作成 - {disease_name}")
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
                    logger.error(f"行 {index + 2}: エラー {str(e)}")
                    errors.append(f"行 {index + 2}: {str(e)}")
                    continue
            
            # コミット
            try:
                db.commit()
                logger.info(f"インポート成功: {imported_count}件のデータをインポートしました。{skipped_count}件スキップしました。")
            except Exception as e:
                db.rollback()
                logger.error(f"データベースエラー: {str(e)}")
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
            logger.error(f"予期せぬエラー: {str(e)}")
            return {
                "status": "error",
                "message": f"予期せぬエラー: {str(e)}",
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
