import sqlite3
import os

def check_db_structure(db_path):
    """既存のデータベース構造を確認"""
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # テーブル一覧を取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("=== Tables in the database ===")
    for table in tables:
        print(f"Table: {table[0]}")
        
        # テーブルのスキーマを表示
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        
        print("Columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")
        
        # データのサンプルを表示
        cursor.execute(f"SELECT * FROM {table[0]} LIMIT 5;")
        data = cursor.fetchall()
        
        if data:
            print(f"Sample data (first {len(data)} rows):")
            for row in data:
                print(f"  {row}")
        else:
            print("  No data in this table")
        
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    db_path = "disease_support.db"
    check_db_structure(db_path)
