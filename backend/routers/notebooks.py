from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import Notebook, Document
from backend.schemas import NotebookCreate, NotebookResponse, DocumentResponse
import json

router = APIRouter()

@router.post("/", response_model=NotebookResponse)
def create_notebook(notebook: NotebookCreate, db: Session = Depends(get_db)):
    """Create a new notebook"""
    db_notebook = Notebook(name=notebook.name, description=notebook.description)
    db.add(db_notebook)
    db.commit()
    db.refresh(db_notebook)
    return db_notebook

@router.get("/")
def list_notebooks(db: Session = Depends(get_db)):
    """List all notebooks"""
    notebooks = db.query(Notebook).order_by(Notebook.created_at.desc()).all()
    
    # Add document count to each notebook
    result = []
    for notebook in notebooks:
        notebook_dict = {
            "id": notebook.id,
            "name": notebook.name,
            "description": notebook.description,
            "created_at": notebook.created_at,
            "updated_at": notebook.updated_at,
            "document_count": db.query(Document).filter(Document.notebook_id == notebook.id).count()
        }
        result.append(notebook_dict)
    
    return result

@router.get("/{notebook_id}", response_model=NotebookResponse)
@router.get("/{notebook_id}/", response_model=NotebookResponse)
def get_notebook(notebook_id: int, db: Session = Depends(get_db)):
    """Get a specific notebook"""
    notebook = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook

@router.get("/{notebook_id}/documents", response_model=List[DocumentResponse])
@router.get("/{notebook_id}/documents/", response_model=List[DocumentResponse])
def get_notebook_documents(notebook_id: int, db: Session = Depends(get_db)):
    """Get all documents in a notebook"""
    documents = db.query(Document).filter(Document.notebook_id == notebook_id).all()
    return documents

@router.delete("/{notebook_id}")
def delete_notebook(notebook_id: int, db: Session = Depends(get_db)):
    """Delete a notebook"""
    notebook = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    db.delete(notebook)
    db.commit()
    return {"message": "Notebook deleted successfully"}
