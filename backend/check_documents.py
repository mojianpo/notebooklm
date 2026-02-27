"""
检查数据库中的文档状态和内容
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Document, Notebook

def check_documents():
    db = SessionLocal()
    try:
        notebooks = db.query(Notebook).all()
        print(f"\n=== 找到 {len(notebooks)} 个笔记本 ===\n")
        
        for notebook in notebooks:
            print(f"笔记本 ID: {notebook.id}, 名称: {notebook.name}")
            documents = db.query(Document).filter(Document.notebook_id == notebook.id).all()
            print(f"  文档数量: {len(documents)}")
            
            for doc in documents:
                content_length = len(doc.content) if doc.content else 0
                print(f"  - 文档 ID: {doc.id}")
                print(f"    文件名: {doc.filename}")
                print(f"    状态: {doc.status}")
                print(f"    内容长度: {content_length} 字符")
                if doc.content:
                    print(f"    内容预览: {doc.content[:100]}...")
                else:
                    print(f"    内容: 无内容")
                print()
    
    finally:
        db.close()

if __name__ == "__main__":
    check_documents()
