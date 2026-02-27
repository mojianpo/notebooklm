"""
检查所有文档状态
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Document

def check_all_documents():
    db = SessionLocal()
    try:
        all_docs = db.query(Document).all()
        print(f"\n=== 数据库中共有 {len(all_docs)} 个文档 ===\n")
        
        for doc in all_docs:
            content_length = len(doc.content) if doc.content else 0
            print(f"文档 ID: {doc.id}")
            print(f"  笔记本 ID: {doc.notebook_id}")
            print(f"  文件名: {doc.filename}")
            print(f"  状态: {doc.status}")
            print(f"  内容长度: {content_length} 字符")
            print(f"  文件类型: {doc.file_type}")
            print()
    
    finally:
        db.close()

if __name__ == "__main__":
    check_all_documents()
