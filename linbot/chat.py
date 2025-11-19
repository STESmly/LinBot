from typing import Callable, TypeAlias, Awaitable, Optional
from functools import wraps
import pydantic
import inspect
from message_type import Messgaechat,chat_type

class register_meta(pydantic.BaseModel):
    name: str = None
    block: bool = False
    """是否阻塞后续函数调用"""
    on_msg: Optional[Callable] = Messgaechat.on_message

    class Config:
        extra = "allow"
    

class event_message(pydantic.BaseModel):
    roomid: int = None
    """房间id"""  # 房间的唯一标识符，用于区分不同的直播间
    username: str = None
    """用户名"""  # 发送消息的用户昵称
    uid: int = None
    """用户id"""  # 用户的唯一标识符，用于区分不同的用户
    msg: str = None
    """普通弹幕消息内容"""  # 用户发送的普通弹幕文本内容
    commandargs: Optional[str] = None
    """除指令外剩余的参数，适用于指令+参数的情况"""


ExperFn: TypeAlias = Callable[..., Awaitable[None]]

fun_call_list: list[dict] = []

def fun_call_register(name: str=None, *fun_arg, **fun_kwarg) -> Callable[[ExperFn], ExperFn]:
    def decorator(func: ExperFn) -> ExperFn:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            return await func(*args, **kwargs)
        
        signature = inspect.signature(func)
        param_types = {}
        for param_name, param in signature.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                param_types[param_name] = param.annotation
        
        fun_arg_data = register_meta(*fun_arg, **fun_kwarg)
        fun_call_list.append({
            'name': name,
            'wrapper': wrapper, 
            'fun_arg': fun_arg_data,
            'param_types': param_types
        })
        return wrapper
    return decorator

async def fun_call(fun_name: str, *args, **kwargs) -> None:
    event_arg = None
    for arg in args:
        if isinstance(arg, event_message):
            event_arg = arg
            break
    
    for key, value in kwargs.items():
        if isinstance(value, event_message):
            event_arg = value
            break
    
    for value in fun_call_list:
        name = value.get("name")
        func = value.get("wrapper")
        param_types: dict = value.get("param_types")
        fun_args: register_meta = value.get("fun_arg")
        
        match_result:chat_type = fun_args.on_msg(name, fun_name)
        
        if match_result.type:
            updated_event = event_message(
                roomid=event_arg.roomid if event_arg else None,
                username=event_arg.username if event_arg else None,
                uid=event_arg.uid if event_arg else None,
                msg=event_arg.msg if event_arg else None,
                commandargs=match_result.commandargs
            )
            
            matched_kwargs = {}
            
            for param_name, param_type in param_types.items():
                found_arg = None
                for arg in args:
                    if isinstance(arg, param_type):
                        if param_type == event_message:
                            found_arg = updated_event
                        else:
                            found_arg = arg
                        break
                
                if found_arg:
                    matched_kwargs[param_name] = found_arg
            
            for key, val in kwargs.items():
                if key in param_types:
                    if param_types[key] == event_message:
                        matched_kwargs[key] = updated_event
                    else:
                        matched_kwargs[key] = val
            
            if event_message in param_types.values() and not any(isinstance(arg, event_message) for arg in matched_kwargs.values()):
                for param_name, param_type in param_types.items():
                    if param_type == event_message:
                        matched_kwargs[param_name] = updated_event
                        break
            
            if fun_args.block:
                await func(**matched_kwargs)
                break
            else:
                await func(**matched_kwargs)