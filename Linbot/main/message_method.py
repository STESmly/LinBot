# main/message_method.py
import asyncio
import json
import uuid
from typing import Optional
from logger import Logging
from event import SendReturn, GroupMessageEvent, PrivateMessageEvent
from context import get_current_event, get_current_websocket
from onebot_protocol import OneBotProtocol
from response_handler import response_handler

logger = Logging.logger

class MessageSender:
    def __init__(self):
        pass
    
    async def _send_and_wait(self, data: dict) -> Optional[SendReturn]:
        """发送消息并等待响应"""
        ws = get_current_websocket()
        if not ws:
            logger.error("WebSocket 未连接")
            return None
        
        echo = str(uuid.uuid4())
        data["echo"] = echo
        
        try:
            # 先准备等待响应
            response_task = asyncio.create_task(response_handler.wait_for_response(echo))
            
            # 然后发送消息
            await ws.send_str(json.dumps(data))
            
            # 等待响应
            response_data = await response_task
            return SendReturn(**response_data)
            
        except asyncio.TimeoutError:
            logger.error(f"等待响应超时，echo: {echo}")
            return None
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return None
    
    async def send_group_msg(self, message: list, group_id: Optional[int] = None) -> Optional[SendReturn]:
        """发送群消息"""
        if group_id is None:
            current_event = get_current_event()
            if current_event and hasattr(current_event, 'group_id'):
                group_id = current_event.group_id
            elif isinstance(current_event, GroupMessageEvent):
                group_id = current_event.group_id
            else:
                logger.error("未指定 group_id 且无法从当前事件获取")
                return None
        
        action_data = OneBotProtocol.create_group_message(group_id, message)
        response = await self._send_and_wait(action_data)
        
        if response:
            logger.success(f"群消息发送成功: {response.status}")
        else:
            logger.error("群消息发送失败")
        return response
    
    async def send_private_msg(self, message:list, user_id: Optional[int] = None) -> Optional[SendReturn]:
        """发送私聊消息"""
        if user_id is None:
            current_event = get_current_event()
            if current_event and hasattr(current_event, 'user_id'):
                user_id = current_event.user_id
            elif isinstance(current_event, PrivateMessageEvent):
                user_id = current_event.user_id
            else:
                logger.error("未指定 user_id 且无法从当前事件获取")
                return None
        
        action_data = OneBotProtocol.create_private_message(user_id, message)
        response = await self._send_and_wait(action_data)
        
        if response:
            logger.success(f"私聊消息发送成功: {response.status}")
        else:
            logger.error("私聊消息发送失败")
        return response

# 全局实例
message_sender = MessageSender()

# 用户API
async def send_group_msg(message: list, group_id: Optional[int] = None) -> Optional[SendReturn]:
    return await message_sender.send_group_msg(message, group_id)

async def send_private_msg(message: list, user_id: Optional[int] = None) -> Optional[SendReturn]:
    return await message_sender.send_private_msg(message, user_id)