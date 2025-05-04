import pandas as pd
import sys
from pathlib import Path

def analyze_nando_file(file_path):
    """NANDOファイルの詳細な構造分析"""
    print(f"Analyzing: {file_path}")
    print("=" * 50)
    
    try:
        # Excelファイルを読み込み
        xls = pd.ExcelFile(file_path)
        print(f"Sheet names: {xls.sheet_names}")
        print("=" * 50)
        
        # 各シートの内容を詳しく確認
        for sheet_name in xls.sheet_names:
            print(f"\n=== Sheet: {sheet_name} ===")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            print(f"Shape: {df.shape}")
            print(f"\nColumns: {list(df.columns)}")
            
            # データ型を表示
            print(f"\nData types:")
            print(df.dtypes)
            
            # 最初の5行を表示
            print(f"\nFirst 5 rows:")
            print(df.head())
            
            # 各カラムのユニークな値の数
            print(f"\nUnique values per column:")
            for col in df.columns:
                unique_count = df[col].nunique()
                print(f"  {col}: {unique_count} unique values")
            
            # IDカラムがある場合、パターンを確認
            id_columns = [col for col in df.columns if 'id' in col.lower() or 'ID' in col.lower()]
            if id_columns:
                for id_col in id_columns:
                    print(f"\nSample IDs from {id_col}:")
                    print(df[id_col].dropna().head(10).tolist())
            
            # 病名関連のカラムを探す
            name_columns = [col for col in df.columns if '病' in col or '疾患' in col or 'name' in col.lower()]
            if name_columns:
                for name_col in name_columns:
                    print(f"\nSample disease names from {name_col}:")
                    print(df[name_col].dropna().head(10).tolist())
            
            print("\n" + "-" * 50)
            
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    # コマンドライン引数からファイルパスを取得
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "nando.xlsx"
    
    if Path(file_path).exists():
        analyze_nando_file(file_path)
    else:
        print(f"File not found: {file_path}")
