# main/_event_logger.py
from typing import Callable, TypeAlias, Awaitable
from functools import wraps
from event import *
from logger import Logging, Colors
from message_method import send_group_msg

logger = Logging.logger

ExperFn: TypeAlias = Callable[..., Awaitable[None]]

fun_call_list: dict = {}

def loggermanage(name: str=None) -> Callable[[ExperFn], ExperFn]:
    def decorator(func: ExperFn) -> ExperFn:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            return await func(*args, **kwargs)
        
        fun_call_list[name] = wrapper
        return wrapper
    return decorator

async def call_logger(fun_name: str, event: base_event) -> None:
    if fun_name in fun_call_list:
        func = fun_call_list[fun_name]
        await func(event)
    else:
        logger.warning(f"{fun_name} 暂不支持")
    
@loggermanage("message")
async def _(event: MessageEvent) -> None:
    if event.message_type == "group":
        event: GroupMessageEvent = event
        logger.success(f"[{event.message_type}.{event.sub_type}] 来自用户 {event.user_id} @群 {event.group_id} 的消息： {Colors.BLUE}{event.raw_message}{Colors.END}")
        # 测试消息发送 - 现在应该可以正常工作了
        # await send_group_msg(f"收到来自用户 {event.user_id} @群 {event.group_id} 的消息： {event.raw_message}")
    elif event.message_type == "private":
        event: PrivateMessageEvent = event
        if event.sub_type == "friend":
            logger.success(f"[{event.message_type}.{event.sub_type}] 来自好友 {event.user_id} 的消息： {Colors.BLUE}{event.raw_message}{Colors.END}")
        elif event.sub_type == "group":
            logger.success(f"[{event.message_type}.{event.sub_type}] 来自用户 {event.user_id} @群 {event.sender.group_id} 的临时会话： {Colors.BLUE}{event.raw_message}{Colors.END}")

@loggermanage("message_sent")
async def _(event: MessageEvent) -> None:
    if event.message_type == "group":
        event: GroupMessageEvent = event
        logger.success(f"[{event.message_type}.{event.sub_type}] bot向群 {event.group_id} 发送消息： {Colors.BLUE}{event.raw_message}{Colors.END}")
    elif event.message_type == "private":
        event: PrivateMessageEvent = event
        if event.sender.group_id :
            logger.success(f"[{event.message_type}.{event.sub_type}] bot向用户 {event.target_id} @群 {event.sender.group_id} 发送临时会话消息： {Colors.BLUE}{event.raw_message}{Colors.END}")
        else:
            logger.success(f"[{event.message_type}.{event.sub_type}] bot向用户 {event.target_id} 发送好友消息： {Colors.BLUE}{event.raw_message}{Colors.END}")

@loggermanage("meta_event")
async def _(event: base_event) -> None:
    logger.debug("[心跳]")