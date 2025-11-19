from aiohttp import web
import aiohttp,json
import asyncio
from chat import fun_call #b站弹幕监听直接移植的，暂未适配
from event import base_event
from _event_logger import call_logger,logger
from message_method import message_sender

connected_clients = set()

class WebSocketServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        # 设置 WebSocket 路由
        self.app.router.add_get('/onebot/v11/ws', self.websocket_handler)

    async def websocket_handler(self, request):
        # 创建 WebSocket 连接
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # 添加到已连接客户端集合
        connected_clients.add(ws)
        logger.info(f"新的 WebSocket 连接建立。当前连接数: {len(connected_clients)}")
        
        try:
            # 处理 WebSocket 消息
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if 'echo' in data:
                        # 这是对之前发送消息的响应
                        message_sender.handle_response(data)
                    else:
                        res = base_event(**data)
                        message_sender.set_websocket(ws)
                        message_sender.set_current_event(res)
                        asyncio.create_task(call_logger(res.post_type, res))
                        #asyncio.create_task(你的指令处理函数(res))
                    
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket 错误: {ws.exception()}")
                    
        except Exception as e:
            logger.warning(f"处理 WebSocket 时发生错误: {e}")
        finally:
            # 连接关闭时移除客户端
            connected_clients.remove(ws)
            logger.info(f"WebSocket 连接关闭。当前连接数: {len(connected_clients)}")
        
        return ws

    #async def broadcast_message(self, message):
        #"""向所有连接的客户端广播消息"""
        #if connected_clients:
            #disconnected_clients = set()
            
            #for ws in connected_clients:
                #try:
                    #await ws.send_str(message)
                #except Exception:
                    #disconnected_clients.add(ws)
            
            # 移除断开连接的客户端
            #for ws in disconnected_clients:
                #connected_clients.remove(ws)

    async def start_server(self, host='localhost', port=8050): #llob等协议端设置反向ws
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"WebSocket 服务器启动在: ws://{host}:{port}/onebot/v11/ws")
        
        # 保持服务器运行
        try:
            while True:
                await asyncio.sleep(3600)  # 每小时检查一次
        except asyncio.exceptions.CancelledError:
            logger.info("服务器关闭")

# 运行服务器
async def main():
    server = WebSocketServer()
    await server.start_server()

asyncio.run(main())