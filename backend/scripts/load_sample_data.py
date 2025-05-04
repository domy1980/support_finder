import sys
import json
from pathlib import Path

# プロジェクトのルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal, engine
from app.models.disease import Disease, Base
from app.services.disease_service import DiseaseService
from app.schemas.disease import DiseaseCreate

# データベーステーブルの作成
Base.metadata.create_all(bind=engine)

def load_sample_data():
    db = SessionLocal()
    disease_service = DiseaseService()
    
    try:
        # サンプルデータの読み込み
        with open(project_root / 'data' / 'sample_diseases.json', 'r', encoding='utf-8') as f:
            diseases = json.load(f)
        
        # データの登録
        for disease_data in diseases:
            disease = DiseaseCreate(**disease_data)
            existing = disease_service.get_disease(db, disease.id)
            if not existing:
                disease_service.create_disease(db, disease)
                print(f"Created disease: {disease.name}")
            else:
                print(f"Disease already exists: {disease.name}")
        
        print("Sample data loaded successfully!")
    
    except Exception as e:
        print(f"Error loading sample data: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    load_sample_data()
