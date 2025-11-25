# main/onebot_protocol.py
import json
from logger import Logging

logger = Logging.logger

class OneBotProtocol:
    """OneBot协议消息格式工具"""
    
    @staticmethod
    def create_group_message(group_id: int, message: list) -> dict:
        """创建群消息"""
        return {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": message
            }
        }
    
    @staticmethod
    def create_private_message(user_id: int, message: list) -> dict:
        """创建私聊消息"""
        return {
            "action": "send_private_msg", 
            "params": {
                "user_id": user_id,
                "message": message
            }
        }
    
    @staticmethod
    def validate_response(response: dict) -> bool:
        """验证响应格式"""
        required_fields = ['status', 'retcode', 'data']
        return all(field in response for field in required_fields)