# main/context.py
import contextvars
from typing import Optional, Any
from aiohttp import web
from event import base_event

# 全局上下文变量
current_event: contextvars.ContextVar[Optional[base_event]] = contextvars.ContextVar('current_event', default=None)
current_websocket: contextvars.ContextVar[Optional[web.WebSocketResponse]] = contextvars.ContextVar('current_websocket', default=None)

class EventContext:
    """事件上下文管理器"""
    
    def __init__(self, event: base_event, websocket: web.WebSocketResponse = None):
        self.event = event
        self.websocket = websocket
        self.event_token = None
        self.websocket_token = None
    
    async def __aenter__(self):
        """异步进入上下文"""
        self.event_token = current_event.set(self.event)
        if self.websocket:
            self.websocket_token = current_websocket.set(self.websocket)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出上下文"""
        if self.event_token:
            current_event.reset(self.event_token)
        if self.websocket_token:
            current_websocket.reset(self.websocket_token)

def get_current_event() -> Optional[base_event]:
    """获取当前事件"""
    return current_event.get()

def get_current_websocket() -> Optional[web.WebSocketResponse]:
    """获取当前 WebSocket 连接"""
    return current_websocket.get()
