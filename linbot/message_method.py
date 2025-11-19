import uuid, json
from logger import Logging
import asyncio
from typing import Optional, Dict, Any
from event import SendReturn

logger = Logging.logger

class MessageSender:
    def __init__(self):
        self.ws = None
        self.current_event = None
        self.response_queues: Dict[str, asyncio.Queue] = {}  # 存储响应队列
    
    def set_websocket(self, ws):
        self.ws = ws
    
    def set_current_event(self, event):
        self.current_event = event

    async def send(self, data:dict) -> Optional[SendReturn]:
        """发送消息的通用函数"""
        echo = str(uuid.uuid4())
        data.update({"echo": echo})
        if self.ws:
            try:
                # 为这个请求创建一个响应队列
                response_queue = asyncio.Queue()
                self.response_queues[echo] = response_queue
                
                # 发送消息
                await self.ws.send_str(json.dumps(data))
                
                # 异步等待响应，不阻塞其他任务
                try:
                    # 设置超时
                    response = await asyncio.wait_for(response_queue.get(), timeout=10.0)
                    return SendReturn(**response)
                except asyncio.TimeoutError:
                    logger.error(f"等待响应超时，echo: {echo}")
                    return None
                finally:
                    # 清理队列
                    if echo in self.response_queues:
                        del self.response_queues[echo]
                    
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                # 清理队列
                if echo in self.response_queues:
                    del self.response_queues[echo]
                return None
    
    async def send_group_msg(self, message: str, group_id: Optional[int] = None) -> Optional[SendReturn]:
        """发送群组消息并等待响应"""
        if group_id is None:
            if self.current_event is None or not hasattr(self.current_event, 'group_id'):
                logger.error(f"错误: 未指定 group_id 且 current_event 无效")
                return None
            group_id = self.current_event.group_id
        
        data = {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": {
                    "type": "text",
                    "data": {
                        "text": message
                    }
                }
            }
        }
        return await self.send(data)
    
    def handle_response(self, response_data: Dict[str, Any]):
        """处理来自 WebSocket 的响应"""
        echo = response_data.get('echo')
        if echo and echo in self.response_queues:
            # 使用 create_task 异步处理响应，避免阻塞 WebSocket 循环
            asyncio.create_task(self._put_response_to_queue(echo, response_data))
    
    async def _put_response_to_queue(self, echo: str, response_data: Dict[str, Any]):
        """将响应放入队列的异步方法"""
        queue = self.response_queues.get(echo)
        if queue:
            await queue.put(response_data)

message_sender = MessageSender()

async def send_group_msg(message: str) -> Optional[SendReturn]:
    return await message_sender.send_group_msg(message)