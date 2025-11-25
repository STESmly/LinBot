# main/response_handler.py
import json
import asyncio
import uuid
from typing import Dict, Any, Optional
from logger import Logging

logger = Logging.logger

class ResponseHandler:
    """独立的响应处理器"""
    
    def __init__(self):
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()
    
    async def wait_for_response(self, echo: str, timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """等待指定 echo 的响应"""
        async with self._lock:
            if echo not in self._pending_requests:
                future = asyncio.Future()
                self._pending_requests[echo] = future
            else:
                future = self._pending_requests[echo]
        
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            async with self._lock:
                if echo in self._pending_requests:
                    del self._pending_requests[echo]
            raise
        except Exception as e:
            async with self._lock:
                if echo in self._pending_requests:
                    del self._pending_requests[echo]
            raise
    
    def handle_response(self, response_data: Dict[str, Any]):
        """处理响应数据"""
        echo = response_data.get('echo')
        if not echo:
            return
        
        async def _process_response():
            async with self._lock:
                if echo in self._pending_requests:
                    future = self._pending_requests[echo]
                    if not future.done():
                        future.set_result(response_data)
                    del self._pending_requests[echo]
                    logger.debug(f"成功处理响应，echo: {echo}")
                else:
                    logger.warning(f"响应到达时没有对应的等待，echo: {echo}")
        
        # 立即处理，不等待
        asyncio.create_task(_process_response())

# 全局响应处理器实例
response_handler = ResponseHandler()