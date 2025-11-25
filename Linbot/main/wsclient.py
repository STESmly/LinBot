# main/wsclient.py
from aiohttp import web
import aiohttp, json
import asyncio
import os
import argparse
from event import base_event, GroupMessageEvent, PrivateMessageEvent, MessageEvent
from _event_logger import call_logger, logger
from message_method import message_sender
from plugins_manager import plugin_manager
from context import EventContext
from response_handler import response_handler

connected_clients = set()

class WebSocketServer:
    def __init__(self, working_dir=None):
        self.app = web.Application()
        self.working_dir = working_dir
        self.setup_routes()
        self.load_plugins()
        
    def load_plugins(self):
        """加载插件"""
        if self.working_dir:
            plugins_base_dir = os.path.join(self.working_dir, 'plugins')
            logger.info(f"工作目录: {self.working_dir}")
        
        logger.info(f"正在从目录加载插件: {plugins_base_dir}")
        
        if not os.path.exists(plugins_base_dir):
            logger.warning(f"插件目录不存在: {plugins_base_dir}")
            try:
                os.makedirs(plugins_base_dir, exist_ok=True)
                logger.info(f"已创建插件目录: {plugins_base_dir}")
            except Exception as e:
                logger.error(f"创建插件目录失败: {e}")
                return
        
        from registry import registry
        registry.clear()
        
        plugin_manager.load_plugins(plugins_base_dir)

    def setup_routes(self):
        self.app.router.add_get('/onebot/v11/ws', self.websocket_handler)

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        connected_clients.add(ws)
        logger.info(f"新的 WebSocket 连接建立。当前连接数: {len(connected_clients)}")
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    # 优先处理响应消息
                    if 'echo' in data:
                        logger.debug(f"处理响应消息: {data}")
                        # 立即同步处理响应
                        response_handler.handle_response(data)
                        continue
                    
                    # 然后处理事件消息
                    else:
                        data = base_event(**data)
                        # 异步处理事件日志
                        asyncio.create_task(call_logger(data.post_type, data))
                        event_obj = self._create_event_object(data)
                        
                        # 异步处理插件事件
                        async with EventContext(event_obj, ws):
                            asyncio.create_task(plugin_manager.handle_event(event_obj.post_type, event_obj))
                    
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket 错误: {ws.exception()}")
                    
        except Exception as e:
            logger.warning(f"处理 WebSocket 时发生错误: {e}")
        finally:
            connected_clients.remove(ws)
            logger.info(f"WebSocket 连接关闭。当前连接数: {len(connected_clients)}")
        
        return ws
    
    def _create_event_object(self, data: base_event):
        """根据数据类型创建对应的事件对象"""
        post_type = data.post_type
        message_type = data.model_dump().get("message_type")
        
        if post_type == 'message':
            if message_type == 'group':
                return GroupMessageEvent(**data.model_dump())
            elif message_type == 'private':
                return PrivateMessageEvent(**data.model_dump())
            else:
                return MessageEvent(**data.model_dump())
        else:
            return data

    async def start_server(self, host='localhost', port=8050):
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"WebSocket 服务器启动在: ws://{host}:{port}/onebot/v11/ws")
        
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.exceptions.CancelledError:
            logger.info("服务器关闭")

async def main():
    parser = argparse.ArgumentParser(description='LinBot WebSocket 服务器')
    parser.add_argument('-p', '--working-dir', help='工作目录路径')
    args = parser.parse_args()
    
    server = WebSocketServer(working_dir=args.working_dir)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())