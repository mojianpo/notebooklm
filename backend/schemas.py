from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Notebook Schemas
class NotebookBase(BaseModel):
    name: str
    description: Optional[str] = None

class NotebookCreate(NotebookBase):
    pass

class NotebookResponse(NotebookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    notebook_id: int
    file_url: str

class DocumentResponse(DocumentBase):
    id: int
    notebook_id: int
    file_url: str
    content: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Conversation Schemas
class ConversationBase(BaseModel):
    notebook_id: int
    title: Optional[str] = "New Conversation"

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    conversation_id: int

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI Chat Request
class ChatRequest(BaseModel):
    notebook_id: int
    conversation_id: Optional[int] = None
    message: str

# AI Content Generation Request
class ContentGenerationRequest(BaseModel):
    notebook_id: int
    content_type: str  # report, mindmap, infographic, flashcards, quiz, podcast, presentation, datatable
    custom_prompt: Optional[str] = None

class ContentGenerationResponse(BaseModel):
    content_type: str
    content: str
    format: str

class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None

class NoteCreate(NoteBase):
    notebook_id: int

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(NoteBase):
    id: int
    notebook_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
