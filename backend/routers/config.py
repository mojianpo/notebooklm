from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from config_model import Config

router = APIRouter()

# Default LLM configurations
DEFAULT_CONFIGS = {
    "llm.model_name": "deepseek-chat",
    "llm.model_id": "deepseek-chat",
    "llm.base_url": "https://api.deepseek.com",
    "llm.api_key": "sk-...",
    "llm.temperature": 0.7,
    "llm.max_tokens": 8000
}

@router.get("/")
def list_configs(db: Session = Depends(get_db), category: Optional[str] = None):
    """List all configurations"""
    query = db.query(Config)
    if category:
        query = query.filter(Config.category == category)
    configs = query.all()
    return [
        {
            "id": config.id,
            "key": config.key,
            "value": config.value,
            "description": config.description,
            "category": config.category,
            "created_at": config.created_at,
            "updated_at": config.updated_at
        }
        for config in configs
    ]

@router.get("/defaults")
def get_default_configs():
    """Get default configuration values"""
    return DEFAULT_CONFIGS

@router.get("/{key}")
def get_config(key: str, db: Session = Depends(get_db)):
    """Get a specific configuration by key"""
    config = db.query(Config).filter(Config.key == key).first()
    if not config:
        # Return default value if not in database
        return {
            "key": key,
            "value": DEFAULT_CONFIGS.get(key),
            "is_default": True
        }
    return {
        "id": config.id,
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "category": config.category,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
        "is_default": False
    }

@router.post("/")
def create_config(key: str, value: str, description: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    """Create or update a configuration"""
    config = db.query(Config).filter(Config.key == key).first()
    if config:
        # Update existing
        config.value = value
        if description:
            config.description = description
        if category:
            config.category = category
    else:
        # Create new
        config = Config(
            key=key,
            value=value,
            description=description,
            category=category or "custom"
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    
    return {
        "id": config.id,
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "category": config.category,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    }

@router.put("/{key}")
def update_config(key: str, value: str, db: Session = Depends(get_db)):
    """Update a configuration"""
    config = db.query(Config).filter(Config.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    config.value = value
    db.commit()
    db.refresh(config)
    
    return {
        "id": config.id,
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "category": config.category,
        "updated_at": config.updated_at
    }

@router.delete("/{key}")
def delete_config(key: str, db: Session = Depends(get_db)):
    """Delete a configuration and reset to default"""
    config = db.query(Config).filter(Config.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db.delete(config)
    db.commit()
    
    return {
        "message": "Configuration deleted",
        "key": key,
        "default_value": DEFAULT_CONFIGS.get(key)
    }

@router.post("/reset")
def reset_to_defaults(keys: Optional[List[str]] = None, db: Session = Depends(get_db)):
    """Reset configurations to default values"""
    if keys:
        # Reset specific keys
        for key in keys:
            config = db.query(Config).filter(Config.key == key).first()
            if config:
                db.delete(config)
    else:
        # Reset all custom configurations
        db.query(Config).filter(Config.category == "llm").delete()
    
    db.commit()
    
    return {
        "message": "Configurations reset to defaults",
        "reset_count": len(keys) if keys else "all"
    }
