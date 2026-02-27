from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Document
from backend.config_model import Config
from backend.schemas import ContentGenerationRequest, ContentGenerationResponse
from backend.config import settings
import json
import asyncio

# 尝试导入 LLM 相关库
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = True

router = APIRouter()

# Get LLM configuration from database
def get_llm_config(db: Session):
    """Get LLM configuration from database"""
    try:
        # Get configs with category 'llm' or 'custom'
        configs = db.query(Config).filter(Config.category.in_(["llm", "custom"])).all()
        llm_config = {}
        for config in configs:
            key = config.key
            # Handle dot notation (llm.api_key) and underscore notation (llm_api_key)
            if key.startswith("llm."):
                # Remove llm. prefix
                normalized_key = key[4:]
                llm_config[normalized_key] = config.value
            elif key.startswith("llm_"):
                # Remove llm_ prefix
                normalized_key = key[4:]
                llm_config[normalized_key] = config.value
            else:
                llm_config[key] = config.value
        
        # Map model_id to model for compatibility with frontend
        if "model_id" in llm_config and "model" not in llm_config:
            llm_config["model"] = llm_config["model_id"]
        
        print(f"LLM configuration: {llm_config}")
        return llm_config
    except Exception as e:
        print(f"Error loading LLM configuration: {e}")
        # Return default configuration if database query fails
        return {}

# Content type prompts
CONTENT_PROMPTS = {
    "report": """
你是一名多学科领域的学术文献分析专家。你的核心任务是：接收用户上传的一篇或多篇学术文献摘要，通过精准的结构化提炼与逻辑化总结，输出其核心学术内容，帮助用户高效把握文献重点，服务于文献调研、论文撰写与课题研究。
一、 核心处理原则
学科适配：自动识别文献所属一级及二级学科（如：计算机科学-机器学习、临床医学-肿瘤学），交叉学科需兼顾。使用准确的专业术语，遵循该学科的学术表达规范。
精准提炼：严格围绕文献摘要内容进行提炼，确保关键信息无遗漏、无偏差。主动剔除“随着…发展”、“综上所述”等无实质信息的冗余表述。
批量处理：处理多篇文献时，为每篇标注独立标识（如文献1、文献2…），并保持各篇输出格式与提炼深度完全一致，便于横向对比。
风格严谨：全程采用“学术严谨型”叙述风格，确保逻辑严密、表述专业。

二、 核心任务流程
请严格按以下两个步骤处理每篇文献：

步骤一：四大核心要素提炼
请从摘要中精准提炼以下四个要素，每个要素后需附上3-5个最能代表该部分内容的核心关键词。
1. 研究背景 (50-80字)：阐述该研究领域的现状、存在的具体问题或知识缺口，以及本研究的意义。关键词应涵盖领域核心与现存问题。
2. 研究目的 (30-50字)：明确陈述本研究旨在达成的核心目标或拟解决的关键科学/实践问题。关键词应包含研究目标与解决对象。
3. 研究方法 (60-90字)：根据学科属性，说明主要研究手段、数据或资料来源、以及使用的关键分析工具、模型或理论框架。
      a) 理工科：侧重实验设计、算法模型、数据指标。
      b) 人文社科：侧重研究方法论（如文献研究法、案例研究）、论证逻辑、理论基础。
      c) 医学：侧重研究设计（如RCT）、样本来源、评价指标。
      d) 经管：侧重实证模型、数据来源、分析软件。

4. 研究结论 (50-80字)：概括研究取得的核心成果、关键发现，及其理论或实践启示/价值。关键词应体现成果核心与应用价值。

步骤二：核心观点总结生成

基于步骤一提炼的四大要素，以逻辑连贯、衔接自然的方式，整合生成一篇400-600字的详细版学术总结。总结需完整覆盖四大要素的核心信息，并将各要素的关键关键词自然融入行文，突出文献的整体贡献与价值脉络。多篇文献则各自独立成篇。

三、 最终输出格式

# 文献名称

## 研究背景  [关键词1], [关键词2], [关键词3...]
### 核心要点  [一句话说明]
   [内容]

## 研究目的  [关键词1], [关键词2], [关键词3...]
### 核心要点  [一句话说明]
   [内容]

## 研究方法  [关键词1], [关键词2], [关键词3...]
### 核心要点  [一句话说明]
   [内容]

## 研究结论  [关键词1], [关键词2], [关键词3...]
### 核心要点  [一句话说明]
   [内容]

## 核心观点总结
### 核心要点  [一句话说明]
  [总结内容]

如果有多篇文档，随后按相同格式输出文献2、文献3…

四、 严格约束
仅输出上述格式要求的内容，不添加任何额外解释、问候或总结性语句。
若摘要中某要素信息缺失，对应内容返回空字符串“”，不自行编造或模糊处理。
严格遵守各模块的字数范围与关键词数量要求，确保表述精炼、准确。
输出的内容严格按照markdown语法格式进行输出，首字符必须为#
    """,
    "mindmap": """
你是一名思维导图专家，擅长将复杂的文档内容转化为清晰的层次结构。请基于提供的文档内容，创建一个详细的思维导图。

要求：
1. 以文档的主要主题为中心节点
2. 层次分明，逻辑清晰
3. 包含文档中的关键概念、观点和结论
4. 使用Markdown标题格式表示层次结构（# 一级节点，## 二级节点，### 三级节点等）
5. 确保覆盖文档的核心内容
6. 输出内容严格按照markdown语法格式进行输出，首字符必须为#

输出格式：
# 中心主题
## 子主题1
### 子主题1.1
### 子主题1.2
## 子主题2
### 子主题2.1
### 子主题2.2
    """,
    "flashcards": """
你是一名教育专家，擅长将复杂的文档内容转化为简洁的闪卡形式。请基于提供的文档内容，创建一组闪卡，用于学习和记忆文档中的关键信息。

要求：
1. 每张三卡包含一个问题和一个答案
2. 问题应该针对文档中的关键概念、事实或观点
3. 答案应该简洁明了，直接来自文档内容
4. 闪卡应该覆盖文档的主要内容
5. 每张闪卡之间用空行分隔

输出格式：
Q: 问题
A: 答案

Q: 另一个问题
A: 另一个答案
    """,
    "quiz": """
你是一名教育评估专家，擅长基于文档内容创建测验题。请基于提供的文档内容，创建一套测验题，用于测试对文档内容的理解。

要求：
1. 包含多种类型的问题（选择题、判断题、简答题）
2. 问题应该针对文档中的关键概念、事实或观点
3. 提供正确答案
4. 确保测验覆盖文档的主要内容

输出格式：
**Question 1:** 问题
A) 选项A
B) 选项B
C) 选项C
D) 选项D
**Correct Answer:** 正确选项

**Question 2:** 问题
**Answer:** 正确答案
    """,
    "podcast": """
你是一名播客脚本作家，擅长将复杂的文档内容转化为生动的对话形式。请基于提供的文档内容，创建一个播客脚本，用于向听众解释文档中的关键内容。

要求：
1. 包含两个主持人的对话
2. 对话应该自然流畅，符合播客的口语化风格
3. 覆盖文档的主要内容和关键观点
4. 对话应该引人入胜，便于听众理解
5. 精简对话内容，避免冗长而复杂的对话，每次对话控制在150字以内

输出格式：
**Host 1:** 对话内容
**Host 2:** 对话内容
**Host 1:** 对话内容
**Host 2:** 对话内容
    """,
    "presentation": """
你是一名演示文稿专家，擅长将复杂的文档内容转化为清晰的幻灯片大纲。请基于提供的文档内容，创建一个演示文稿大纲，用于向观众展示文档中的关键内容。

要求：
1. 包含10-15张幻灯片
2. 每张幻灯片有一个明确的标题
3. 每张幻灯片包含2-4个要点
4. 覆盖文档的主要内容和关键观点
5. 结构清晰，逻辑连贯

输出格式：
**Slide 1:** 标题
- 要点1
- 要点2

**Slide 2:** 标题
- 要点1
- 要点2
- 要点3
    """,
    "datatable": """
你是一名数据分析师，擅长将文档中的数据和信息整理成结构化的表格。请基于提供的文档内容，创建一个或多个表格，用于展示文档中的关键数据和信息。

要求：
1. 表格应该结构清晰，便于阅读
2. 包含适当的列标题
3. 数据应该准确反映文档内容
4. 如果文档中包含多种类型的数据，可以创建多个表格

输出格式：
| 列标题1 | 列标题2 | 列标题3 |
|---------|---------|---------|
| 数据1   | 数据2   | 数据3   |
| 数据4   | 数据5   | 数据6   |
    """,
    "infographic": """
你是一名信息图表设计师，擅长将复杂的文档内容转化为视觉化的信息图表指南。请基于提供的文档内容，创建一个信息图表设计指南，用于指导信息图表的创建。

要求：
1. 包含关键统计数据和数字
2. 描述主要概念和它们之间的关系
3. 提供视觉层次建议
4. 推荐配色方案
5. 确保设计指南能够准确反映文档内容

输出格式：
# 信息图表设计指南

## 关键统计数据和数字
- 数据1
- 数据2
- 数据3

## 主要概念和关系
- 概念1
- 概念2
- 概念3

## 视觉层次建议
- 建议1
- 建议2
- 建议3

## 配色方案推荐
- 颜色1
- 颜色2
- 颜色3
    """,
    "document_analyzer": """
你是一名文档分析专家，擅长对文档进行深入的结构和内容分析。请基于提供的文档内容，进行详细的文档分析。

要求：
1. 分析文档的基本信息（名称、类型、结构深度等）
2. 分析文档的结构（标题层次、章节组织、逻辑流程等）
3. 提取文档的核心内容（主题、关键论点、支持数据、结论等）
4. 评估文档的质量（完整性、一致性、清晰度等）
5. 输出详细的分析报告

输出格式：
## 文档分析报告

### 基本信息
- 文档名称：XXX
- 文档类型：XXX
- 结构深度：X 级

### 文档结构
1. 章节1：XXX
   1.1 子章节1.1
   1.2 子章节1.2
2. 章节2：XXX

### 核心内容
- 主题：XXX
- 关键论点：
  1. 论点1
  2. 论点2
- 重要数据：XXX

### 质量评估
- 完整性：XXX
- 一致性：XXX
- 清晰度：XXX
    """
}

# Generate content based on document content and custom prompt
def generate_content_with_llm(content_type: str, documents: list, custom_prompt: str = None, db: Session = None):
    """Generate content using LLM based on document content and custom prompt"""
    # Extract document content and filenames
    document_filenames = [doc.filename for doc in documents]
    document_contents = [doc.content for doc in documents if doc.content]
    
    # Assemble document content
    document_text = "\n\n".join([f"# {filename}\n\n{content}" for filename, content in zip(document_filenames, document_contents)])
    
    # Get base prompt
    base_prompt = CONTENT_PROMPTS.get(content_type, "")
    
    # Assemble final prompt
    final_prompt = f"{base_prompt}\n\n## 文档内容：\n{document_text}\n\n"
    if custom_prompt:
        final_prompt += f"## 用户额外要求：\n{custom_prompt}\n"
    
    # If LLM is available, use it to generate content
    if LLM_AVAILABLE and db:
        try:
            # Get LLM configuration from database
            llm_config = get_llm_config(db)
            print(llm_config)
            
            # Get API key from config
            api_key = llm_config.get("api_key")
            
            # Check if API key is provided
            if not api_key:
                print("API key not found in configuration.")
                # Raise exception if API key is not provided
                raise HTTPException(status_code=400, detail="API key not found in configuration. Please set it in the settings.")
            
            # Initialize LLM client with configuration parameters
            llm = ChatOpenAI(
                api_key=api_key,
                model_name=llm_config["model"],
                temperature=float(llm_config["temperature"]),
                max_tokens=int(llm_config["max_tokens"]),
                base_url=llm_config.get("base_url")
            )
            
            # Generate content using LLM
            messages = [
                SystemMessage(content="You are an AI assistant specialized in content generation based on documents."),
                HumanMessage(content=final_prompt)
            ]
            
            # Get response from LLM
            response = llm.invoke(messages)
            
            # Extract content from response
            return response.content
        except HTTPException:
            raise
        except Exception as e:
            print(f"LLM generation failed: {e}")
            # Raise exception if LLM fails
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
    else:
        # Raise exception if LLM is not available
        raise HTTPException(status_code=503, detail="LLM service is not available. Please install required dependencies.")

# Stream generate content using LLM
def stream_generate_content_with_llm(content_type: str, documents: list, custom_prompt: str = None, db: Session = None):
    """Stream generate content using LLM based on document content and custom prompt"""
    # Extract document content and filenames
    document_filenames = [doc.filename for doc in documents]
    document_contents = [doc.content for doc in documents if doc.content]
    
    # Assemble document content
    document_text = "\n\n".join([f"# {filename}\n\n{content}" for filename, content in zip(document_filenames, document_contents)])
    
    # Get base prompt
    base_prompt = CONTENT_PROMPTS.get(content_type, "")
    
    # Assemble final prompt
    final_prompt = f"{base_prompt}\n\n## 文档内容：\n{document_text}\n\n"
    if custom_prompt:
        final_prompt += f"## 用户额外要求：\n{custom_prompt}\n"
    
    # If LLM is available, use it to generate content
    if LLM_AVAILABLE and db:
        try:
            # Get LLM configuration from database
            llm_config = get_llm_config(db)
            
            # Get API key from config
            api_key = llm_config.get("api_key")
            
            # Check if API key is provided
            if not api_key:
                print("API key not found in configuration.")
                # Raise exception if API key is not provided
                yield f"data: {{\"type\": \"error\", \"content\": \"API key not found in configuration. Please set it in the settings.\"}}\n\n"
                return
            
            # Initialize LLM client with configuration parameters
            llm = ChatOpenAI(
                api_key=api_key,
                model_name=llm_config["model"],
                temperature=float(llm_config["temperature"]),
                max_tokens=int(llm_config["max_tokens"]),
                base_url=llm_config.get("base_url"),
                streaming=True  # Enable streaming
            )
            
            # Generate content using LLM with streaming
            messages = [
                SystemMessage(content="You are an AI assistant specialized in content generation based on documents."),
                HumanMessage(content=final_prompt)
            ]
            
            # Stream response from LLM
            for chunk in llm.stream(messages):
                if chunk.content:
                    # Escape special characters for JSON
                    escaped_content = chunk.content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                    yield f"data: {{\"type\": \"content\", \"content\": \"{escaped_content}\"}}\n\n"
            return
        except Exception as e:
            print(f"LLM generation failed: {e}")
            # Return error message if LLM fails
            yield f"data: {{\"type\": \"error\", \"content\": \"LLM generation failed: {str(e)}\"}}\n\n"
            return
    else:
        # Return error message if LLM is not available
        yield f"data: {{\"type\": \"error\", \"content\": \"LLM service is not available. Please install required dependencies.\"}}\n\n"
        return

@router.post("/generate", response_model=ContentGenerationResponse)
@router.post("/generate/", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest, db: Session = Depends(get_db)):
    """Generate various types of content from documents"""
    
    # Validate content type
    if request.content_type not in CONTENT_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Supported types: {', '.join(CONTENT_PROMPTS.keys())}"
        )
    
    # Get documents for the notebook
    documents = db.query(Document).filter(
        Document.notebook_id == request.notebook_id,
        Document.status == "completed"
    ).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found in this notebook")
    
    # Generate content based on document content, custom prompt, and LLM
    generated_content = generate_content_with_llm(request.content_type, documents, request.custom_prompt, db)
    
    return ContentGenerationResponse(
        content_type=request.content_type,
        content=generated_content,
        format="markdown"
    )

from fastapi.responses import StreamingResponse

@router.post("/stream")
@router.post("/stream/")
async def stream_generate_content(request: ContentGenerationRequest, db: Session = Depends(get_db)):
    """Stream generate content from documents"""
    
    # Validate content type
    if request.content_type not in CONTENT_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Supported types: {', '.join(CONTENT_PROMPTS.keys())}"
        )
    
    # Get documents for the notebook
    documents = db.query(Document).filter(
        Document.notebook_id == request.notebook_id,
        Document.status == "completed"
    ).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found in this notebook")
    
    def generate():
        # Stream generate content using LLM
        for chunk in stream_generate_content_with_llm(request.content_type, documents, request.custom_prompt, db):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/types/")
def get_content_types():
    """Get list of supported content generation types"""
    return {
        "types": [
            {"id": "report", "name": "Report", "description": "Comprehensive structured report"},
            {"id": "mindmap", "name": "Mind Map", "description": "Hierarchical mind map structure"},
            {"id": "flashcards", "name": "Flashcards", "description": "Memory cards for learning"},
            {"id": "quiz", "name": "Quiz", "description": "Test questions and answers"},
            {"id": "podcast", "name": "Podcast Script", "description": "Conversational podcast dialogue"},
            {"id": "presentation", "name": "Presentation", "description": "Slide deck outline"},
            {"id": "datatable", "name": "Data Table", "description": "Structured data tables"},
            {"id": "infographic", "name": "Infographic", "description": "Visual content guide"},
            {"id": "document_analyzer", "name": "Document Analyzer", "description": "Deep document structure analysis and content understanding"}
        ]
    }
