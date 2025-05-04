import pandas as pd
import os
from pathlib import Path

def analyze_nando_file(file_path):
    """NANDOファイルの構造を分析"""
    print(f"Analyzing: {file_path}")
    
    try:
        # Excelファイルを読み込み
        xls = pd.ExcelFile(file_path)
        print(f"Sheet names: {xls.sheet_names}")
        
        # 各シートの内容を確認
        for sheet_name in xls.sheet_names:
            print(f"\n=== Sheet: {sheet_name} ===")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print(f"First few rows:")
            print(df.head())
            
            # 特定のカラムがある場合は詳細を表示
            if 'ID' in df.columns or 'id' in df.columns:
                id_col = 'ID' if 'ID' in df.columns else 'id'
                print(f"\nID patterns:")
                print(df[id_col].head(10))
    
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    # NANDOファイルのパスを指定してください
    nando_path = Path("data/nando/nando.xlsx")  # 実際のファイルパスに変更してください
    
    if nando_path.exists():
        analyze_nando_file(nando_path)
    else:
        print(f"File not found: {nando_path}")
        print("Please place the NANDO file in the data/nando directory")
