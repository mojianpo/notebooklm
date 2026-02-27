from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import websockets
import json
import struct
import uuid
from backend.database import get_db
from backend.config import settings
from backend.config_model import Config

router = APIRouter()

PODCAST_API_URL = "wss://openspeech.bytedance.com/api/v3/sami/podcasttts"
RESOURCE_ID = "volc.service_type.10050"
APP_KEY = "aGjiRDfUWi"

DEFAULT_SPEAKERS = ["zh_female_mizaitongxue_v2_saturn_bigtts", "zh_male_dayixiansheng_v2_saturn_bigtts"]

class EventType:
    ConnectionStart = 1
    ConnectionStarted = 50
    ConnectionFinished = 52
    StartSession = 100
    SessionStarted = 150
    FinishSession = 102
    SessionFinished = 152
    UsageResponse = 154
    PodcastRoundStart = 360
    PodcastRoundResponse = 361
    PodcastRoundEnd = 362
    PodcastEnd = 363
    FinishConnection = 2

class MsgType:
    FullClientRequest = 0x01
    AudioOnlyServer = 0x0B
    FullServerResponse = 0x09
    Error = 0x0F

def get_podcast_config(db: Session):
    """从数据库获取播客API配置"""
    try:
        configs = db.query(Config).filter(Config.category.in_(["podcast", "doubao", "custom"])).all()
        podcast_config = {}
        for config in configs:
            key = config.key
            if key.startswith("podcast."):
                normalized_key = key[8:]
                podcast_config[normalized_key] = config.value
            elif key.startswith("podcast_"):
                normalized_key = key[8:]
                podcast_config[normalized_key] = config.value
            elif key.startswith("doubao."):
                normalized_key = key[7:]
                podcast_config[normalized_key] = config.value
            elif key.startswith("doubao_"):
                normalized_key = key[7:]
                podcast_config[normalized_key] = config.value
            else:
                podcast_config[key] = config.value
        return podcast_config
    except Exception as e:
        print(f"加载播客配置失败: {e}")
        return {}

def get_speakers_from_config(podcast_config: dict) -> list:
    """从配置中获取发音人列表"""
    speakers_str = podcast_config.get("speakers")
    if speakers_str:
        try:
            speakers = json.loads(speakers_str)
            if isinstance(speakers, list) and len(speakers) >= 2:
                return speakers[:2]
        except:
            pass
    
    speaker1 = podcast_config.get("speaker1") or podcast_config.get("speaker_1")
    speaker2 = podcast_config.get("speaker2") or podcast_config.get("speaker_2")
    
    if speaker1 and speaker2:
        return [speaker1, speaker2]
    
    return DEFAULT_SPEAKERS

class Message:
    def __init__(self, msg_type: int, event: int, payload: bytes, session_id: str = ""):
        self.type = msg_type
        self.event = event
        self.payload = payload
        self.session_id = session_id

def build_header(msg_type: int, event: int = 0) -> bytes:
    """构建消息头"""
    header = bytearray(4)
    header[0] = 0x11  # version=1, header_size=1
    if event > 0:
        header[1] = (msg_type << 4) | 0x04  # with event
    else:
        header[1] = (msg_type << 4) | 0x00
    header[2] = 0x10  # JSON serialization
    header[3] = 0x00  # reserved
    return bytes(header)

async def send_message(websocket, msg_type: int, event: int, session_id: str, payload: bytes):
    """发送消息"""
    message = bytearray()
    message.extend(build_header(msg_type, event))
    
    if event > 0:
        message.extend(struct.pack('!I', event))
    
    if session_id:
        session_id_bytes = session_id.encode('utf-8')
        message.extend(struct.pack('!I', len(session_id_bytes)))
        message.extend(session_id_bytes)
    
    message.extend(struct.pack('!I', len(payload)))
    message.extend(payload)
    
    await websocket.send(bytes(message))

async def start_connection(websocket):
    """开始连接"""
    await send_message(websocket, MsgType.FullClientRequest, EventType.ConnectionStart, "", b'{}')

async def start_session(websocket, payload: bytes, session_id: str):
    """开始会话"""
    await send_message(websocket, MsgType.FullClientRequest, EventType.StartSession, session_id, payload)

async def finish_session(websocket, session_id: str):
    """结束会话"""
    await send_message(websocket, MsgType.FullClientRequest, EventType.FinishSession, session_id, b'{}')

async def finish_connection(websocket):
    """结束连接"""
    await send_message(websocket, MsgType.FullClientRequest, EventType.FinishConnection, "", b'{}')

async def receive_message(websocket) -> Message:
    """接收消息"""
    data = await websocket.recv()
    
    if isinstance(data, bytes):
        if len(data) < 4:
            return Message(0, 0, data)
        
        msg_type = (data[1] >> 4) & 0x0F
        serialization = (data[2] >> 4) & 0x0F
        
        if msg_type == MsgType.Error:
            if len(data) >= 8:
                error_code = struct.unpack('!I', data[4:8])[0]
                error_payload = data[8:] if len(data) > 8 else b''
                return Message(MsgType.Error, error_code, error_payload)
            return Message(MsgType.Error, 0, data)
        
        if len(data) < 8:
            return Message(msg_type, 0, data)
        
        event = struct.unpack('!I', data[4:8])[0]
        
        if len(data) < 12:
            return Message(msg_type, event, b'')
        
        session_id_len = struct.unpack('!I', data[8:12])[0]
        
        if len(data) < 12 + session_id_len + 4:
            return Message(msg_type, event, b'')
        
        payload_len_offset = 12 + session_id_len
        payload_len = struct.unpack('!I', data[payload_len_offset:payload_len_offset+4])[0]
        
        payload_start = payload_len_offset + 4
        payload = data[payload_start:payload_start+payload_len]
        
        session_id = data[12:12+session_id_len].decode('utf-8') if session_id_len > 0 else ""
        
        return Message(msg_type, event, payload, session_id)
    
    return Message(0, 0, data.encode() if isinstance(data, str) else data)

async def wait_for_event(websocket, expected_type: int, expected_event: int) -> Message:
    """等待特定事件"""
    while True:
        msg = await receive_message(websocket)
        if msg.type == MsgType.Error:
            raise RuntimeError(f"Server error: {msg.payload.decode()}")
        if msg.type == expected_type and msg.event == expected_event:
            return msg

async def generate_podcast_audio(podcast_script: str, app_id: str, access_key: str, speakers: list):
    """生成播客音频"""
    lines = podcast_script.strip().split('\n')
    nlp_texts = []
    
    speaker1 = speakers[0] if len(speakers) > 0 else DEFAULT_SPEAKERS[0]
    speaker2 = speakers[1] if len(speakers) > 1 else DEFAULT_SPEAKERS[1]
    
    for line in lines:
        line = line.strip()
        if line.startswith('**Host 1:**'):
            text = line.replace('**Host 1:**', '').strip()
            if text:
                nlp_texts.append({"text": text, "speaker": speaker1})
        elif line.startswith('**Host 2:**'):
            text = line.replace('**Host 2:**', '').strip()
            if text:
                nlp_texts.append({"text": text, "speaker": speaker2})
    
    if not nlp_texts:
        raise HTTPException(status_code=400, detail="无效的播客脚本格式")
    
    headers = {
        "X-Api-App-Id": app_id,
        "X-Api-App-Key": APP_KEY,
        "X-Api-Access-Key": access_key,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Connect-Id": str(uuid.uuid4()),
    }
    
    websocket = None
    podcast_audio = bytearray()
    
    try:
        websocket = await websockets.connect(PODCAST_API_URL, additional_headers=headers)
        print("WebSocket连接成功")
        
        await start_connection(websocket)
        await wait_for_event(websocket, MsgType.FullServerResponse, EventType.ConnectionStarted)
        print("连接已建立")
        
        session_id = str(uuid.uuid4())
        
        req_params = {
            "input_id": str(uuid.uuid4()),
            "action": 3,
            "use_head_music": False,
            "use_tail_music": False,
            "audio_config": {
                "format": "mp3",
                "sample_rate": 24000,
                "speech_rate": 0
            },
            "nlp_texts": nlp_texts,
            "speaker_info": {
                "random_order2": False,
                "speakers": [speaker1, speaker2]
            }
        }
        
        await start_session(websocket, json.dumps(req_params).encode('utf-8'), session_id)
        await wait_for_event(websocket, MsgType.FullServerResponse, EventType.SessionStarted)
        print("会话已开始")
        
        await finish_session(websocket, session_id)
        print("会话已结束，开始接收音频")
        
        while True:
            try:
                msg = await receive_message(websocket)
                
                if msg.type == MsgType.AudioOnlyServer and msg.event == EventType.PodcastRoundResponse:
                    podcast_audio.extend(msg.payload)
                    print(f"收到音频数据: {len(msg.payload)} bytes")
                
                elif msg.type == MsgType.Error:
                    error_msg = msg.payload.decode('utf-8') if msg.payload else "Unknown error"
                    raise RuntimeError(f"Server error: {error_msg}")
                
                elif msg.type == MsgType.FullServerResponse:
                    if msg.event == EventType.PodcastRoundStart:
                        data = json.loads(msg.payload.decode('utf-8')) if msg.payload else {}
                        print(f"轮次开始: round_id={data.get('round_id')}, speaker={data.get('speaker')}")
                    
                    elif msg.event == EventType.PodcastRoundEnd:
                        print("轮次结束")
                    
                    elif msg.event == EventType.PodcastEnd:
                        print("播客生成完成")
                        break
                    
                    elif msg.event == EventType.SessionFinished:
                        print("会话完成")
                        break
                    
                    elif msg.event == EventType.UsageResponse:
                        print(f"用量信息: {msg.payload.decode('utf-8') if msg.payload else ''}")
            
            except websockets.exceptions.ConnectionClosedError:
                print("连接已关闭")
                break
        
        if podcast_audio:
            yield bytes(podcast_audio)
    
    except Exception as e:
        print(f"生成音频失败: {e}")
        raise HTTPException(status_code=500, detail=f"音频生成失败: {str(e)}")
    
    finally:
        if websocket:
            try:
                await finish_connection(websocket)
            except:
                pass
            await websocket.close()

@router.post("/generate-audio")
async def generate_podcast_audio_endpoint(
    podcast_script: str = Query(..., description="播客脚本内容"),
    db: Session = Depends(get_db)
):
    """生成播客音频"""
    podcast_config = get_podcast_config(db)
    app_id = podcast_config.get("app_id") or podcast_config.get("appId")
    access_key = podcast_config.get("access_token") or podcast_config.get("access_key") or podcast_config.get("accessToken")
    speakers = get_speakers_from_config(podcast_config)
    
    if not app_id or not access_key:
        raise HTTPException(status_code=400, detail="播客API配置缺失，请在设置中配置豆包语音播客的 APP ID 和 Access Token")
    
    async def audio_generator():
        async for audio_chunk in generate_podcast_audio(podcast_script, app_id, access_key, speakers):
            yield audio_chunk
    
    return StreamingResponse(audio_generator(), media_type="audio/mp3")

@router.post("/convert-script")
async def convert_script_to_audio(request: Request, db: Session = Depends(get_db)):
    """将播客脚本转换为音频"""
    data = await request.json()
    podcast_script = data.get("script")
    
    if not podcast_script:
        raise HTTPException(status_code=400, detail="缺少播客脚本")
    
    podcast_config = get_podcast_config(db)
    app_id = podcast_config.get("app_id") or podcast_config.get("appId")
    access_key = podcast_config.get("access_token") or podcast_config.get("access_key") or podcast_config.get("accessToken")
    speakers = get_speakers_from_config(podcast_config)
    
    if not app_id or not access_key:
        raise HTTPException(status_code=400, detail="播客API配置缺失，请在设置中配置豆包语音播客的 APP ID 和 Access Token")
    
    async def audio_generator():
        async for audio_chunk in generate_podcast_audio(podcast_script, app_id, access_key, speakers):
            yield audio_chunk
    
    return StreamingResponse(audio_generator(), media_type="audio/mp3")

@router.get("/config-status")
async def get_podcast_config_status(db: Session = Depends(get_db)):
    """获取播客配置状态"""
    podcast_config = get_podcast_config(db)
    app_id = podcast_config.get("app_id") or podcast_config.get("appId")
    access_key = podcast_config.get("access_token") or podcast_config.get("access_key") or podcast_config.get("accessToken")
    speakers = get_speakers_from_config(podcast_config)
    
    return {
        "configured": bool(app_id and access_key),
        "has_app_id": bool(app_id),
        "has_access_key": bool(access_key),
        "speakers": speakers
    }
