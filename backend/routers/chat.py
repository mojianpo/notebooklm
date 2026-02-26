from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Generator, Optional
import json
import logging
from datetime import datetime
from database import get_db
from models import Conversation, Message, Document
from schemas import ChatRequest, ConversationCreate, ConversationResponse
from config_model import Config

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

router = APIRouter()
logger = logging.getLogger(__name__)

def get_llm_config(db: Session) -> dict:
    """Get LLM configuration from database"""
    try:
        configs = db.query(Config).filter(Config.category.in_(['llm', 'custom'])).all()
        llm_config = {}
        for config in configs:
            key = config.key
            if key.startswith("llm."):
                normalized_key = key[4:]
                llm_config[normalized_key] = config.value
            elif key.startswith("llm_"):
                normalized_key = key[4:]
                llm_config[normalized_key] = config.value
            else:
                llm_config[key] = config.value
        
        if "model_id" in llm_config and "model" not in llm_config:
            llm_config["model"] = llm_config["model_id"]
        
        logger.info(f"LLM configuration loaded: model={llm_config.get('model')}, base_url={llm_config.get('base_url')}")
        return llm_config
    except Exception as e:
        logger.error(f"Error loading LLM configuration: {e}")
        return {}

def get_text_content(content) -> str:
    """Safely extract text from AIMessage content."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return " ".join(text_parts)
    return str(content)

def escape_json_string(text: str) -> str:
    """Escape special characters for JSON string."""
    return (text
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('\n', '\\n')
        .replace('\r', '\\r')
        .replace('\t', '\\t'))

def get_conversation_history(db: Session, conversation_id: int, max_messages: int = 10) -> List:
    """Get recent conversation history for context."""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(max_messages).all()
    
    history = []
    for msg in reversed(messages):
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            history.append(AIMessage(content=msg.content))
    
    return history

def build_knowledge_context(documents: List[Document], max_chars: int = 8000) -> str:
    """Build knowledge context from documents."""
    context_parts = []
    total_chars = 0
    
    for doc in documents:
        if doc.content:
            doc_content = f"【文档: {doc.filename}】\n{doc.content}"
            if total_chars + len(doc_content) > max_chars:
                remaining = max_chars - total_chars
                if remaining > 200:
                    doc_content = doc_content[:remaining] + "..."
                    context_parts.append(doc_content)
                break
            context_parts.append(doc_content)
            total_chars += len(doc_content)
    
    return "\n\n".join(context_parts) if context_parts else "暂无相关文档内容。"

@router.post("/")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """AI Chat endpoint with streaming response"""
    
    documents = db.query(Document).filter(
        Document.notebook_id == request.notebook_id,
        Document.status == "completed"
    ).all()
    
    knowledge = build_knowledge_context(documents)
    
    conversation_id = None
    if request.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if conversation:
            conversation_id = conversation.id
        else:
            logger.warning(f"Conversation {request.conversation_id} not found, creating new one")
    
    if not conversation_id:
        conversation = Conversation(
            notebook_id=request.notebook_id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id
        logger.info(f"Created new conversation: {conversation_id}")
    
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    system_prompt = f"""你是一位专业的智能助手，致力于为用户提供准确、有帮助的回答。

## 核心能力
- 基于知识库内容提供专业解答
- 保持回答的准确性和可靠性
- 用清晰易懂的方式解释复杂概念

## 回答原则
1. **准确性优先**：确保信息来源可靠，必要时说明依据
2. **结构清晰**：使用标题、列表等方式组织内容
3. **重点突出**：核心观点放在前面，细节补充在后
4. **实用导向**：提供可操作的建议和解决方案

## 格式建议
- 使用 ## 标记主要章节
- 使用 - 或 1. 2. 3. 组织要点
- 重要内容使用 **加粗** 强调
- 代码或命令使用 `代码块` 标记

当前时间：{current_time}"""
    
    user_prompt = f"""## 知识库内容
{knowledge}

## 用户问题
{request.message}

请基于知识库内容回答用户问题，如果知识库中没有相关信息，请如实说明。"""
    
    def generate():
        """Streaming response generator"""
        try:
            if not LLM_AVAILABLE:
                error_message = "LLM 服务不可用，请检查依赖安装"
                logger.error(error_message)
                yield f"data: {json.dumps({'type': 'error', 'message': error_message}, ensure_ascii=False)}\n\n"
                return
            
            llm_config = get_llm_config(db)
            
            api_key = llm_config.get("api_key")
            if not api_key:
                error_message = "未配置 API Key，请在设置中配置"
                logger.error(error_message)
                yield f"data: {json.dumps({'type': 'error', 'message': error_message}, ensure_ascii=False)}\n\n"
                return
            
            model_name = llm_config.get("model", "gpt-3.5-turbo")
            temperature = float(llm_config.get("temperature", 0.7))
            max_tokens = int(llm_config.get("max_tokens", 2000))
            base_url = llm_config.get("base_url")
            
            llm_kwargs = {
                "api_key": api_key,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "streaming": True
            }
            if base_url:
                llm_kwargs["base_url"] = base_url
            
            llm = ChatOpenAI(**llm_kwargs)
            
            messages = [SystemMessage(content=system_prompt)]
            
            if request.conversation_id:
                history = get_conversation_history(db, request.conversation_id, max_messages=6)
                messages.extend(history)
            
            messages.append(HumanMessage(content=user_prompt))
            
            logger.info(f"Starting stream for conversation {conversation_id} with model {model_name}")
            
            assistant_response = ""
            for chunk in llm.stream(messages):
                if chunk.content:
                    assistant_response += chunk.content
                    escaped_content = escape_json_string(chunk.content)
                    yield f"data: {{\"type\": \"content\", \"content\": \"{escaped_content}\"}}\n\n"
            
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_response
            )
            db.add(assistant_message)
            db.commit()
            
            logger.info(f"Completed response for conversation {conversation_id}, length: {len(assistant_response)}")
            
            yield f"data: {{\"type\": \"done\", \"conversation_id\": {conversation_id}}}\n\n"
            
        except Exception as e:
            logger.error(f"Error in chat stream: {e}", exc_info=True)
            error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.get("/conversations/{notebook_id}", response_model=List[ConversationResponse])
def get_conversations(notebook_id: int, db: Session = Depends(get_db)):
    """Get all conversations for a notebook"""
    conversations = db.query(Conversation).filter(
        Conversation.notebook_id == notebook_id
    ).order_by(Conversation.created_at.desc()).all()
    return conversations

@router.get("/messages/{conversation_id}")
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages in a conversation"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    return messages

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete a conversation and its messages"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted successfully"}
