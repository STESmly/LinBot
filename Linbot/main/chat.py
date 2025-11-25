# main/chat.py
from typing import Callable, TypeAlias, Awaitable, Optional
from functools import wraps
import pydantic
import inspect
from message_type import Messgaechat, chat_type
from logger import Logging
from registry import registry
from context import EventContext, get_current_websocket

logger = Logging.logger

class register_meta(pydantic.BaseModel):
    name: str = None
    block: bool = False
    on_msg: Optional[Callable] = Messgaechat.on_message
    event_types: list[str] = None

    class Config:
        extra = "allow"

ExperFn: TypeAlias = Callable[..., Awaitable[None]]

_current_plugin_name = None

def set_current_plugin_name(name: str):
    global _current_plugin_name
    _current_plugin_name = name

def clear_current_plugin_name():
    global _current_plugin_name
    _current_plugin_name = None

def fun_call_register(name: str = None, *fun_arg, **fun_kwarg) -> Callable[[ExperFn], ExperFn]:
    def decorator(func: ExperFn) -> ExperFn:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            # 在函数执行期间保持事件上下文
            event = None
            websocket = get_current_websocket()
            
            for arg in args:
                if isinstance(arg, pydantic.BaseModel) and hasattr(arg, 'post_type'):
                    event = arg
                    break
            
            if event and websocket:
                async with EventContext(event, websocket):
                    return await func(*args, **kwargs)
            elif event:
                async with EventContext(event):
                    return await func(*args, **kwargs)
            else:
                return await func(*args, **kwargs)
        
        # 确定插件名称
        plugin_name = _current_plugin_name or "unknown"
        
        if plugin_name == "unknown":
            try:
                module = inspect.getmodule(func)
                if module and hasattr(module, '__file__'):
                    file_path = module.__file__
                    if 'plugins' in file_path:
                        parts = file_path.split('plugins')
                        if len(parts) > 1:
                            plugin_part = parts[1].lstrip('\\/')
                            if '\\' in plugin_part:
                                plugin_name = plugin_part.split('\\')[0]
                            elif '/' in plugin_part:
                                plugin_name = plugin_part.split('/')[0]
                            else:
                                plugin_name = plugin_part
                        
                        if plugin_name == '__init__.py':
                            plugin_name = '__root__'
                        elif plugin_name.endswith('.py'):
                            plugin_name = plugin_name[:-3]
            except Exception as e:
                logger.debug(f"推断插件名称失败: {e}")
        
        # 创建 register_meta 实例
        fun_arg_data = register_meta(name=name, *fun_arg, **fun_kwarg)
        
        # 注册函数
        func_id = registry.register(wrapper, name, plugin_name, fun_arg_data=fun_arg_data)
        
        # 保存注册信息到包装函数
        wrapper._fun_call_register_meta = {
            'id': func_id,
            'name': name,
            'plugin': plugin_name,
            'fun_arg': fun_arg_data
        }
        
        return wrapper
    return decorator

def _is_event_matching(event: pydantic.BaseModel, param_annotations: dict) -> bool:
    """检查事件是否匹配函数的参数类型要求"""
    if not any(param_annotations.values()):
        return True
    
    for param_name, annotation in param_annotations.items():
        if annotation is None:
            continue
            
        if (inspect.isclass(annotation) and 
            issubclass(annotation, pydantic.BaseModel)):
            if isinstance(event, annotation):
                return True
            elif event.__class__.__name__ == annotation.__name__:
                return True
            elif annotation.__name__ == 'base_event':
                return True
    
    return False

async def fun_call(event: pydantic.BaseModel) -> None:
    """根据事件类型调用匹配的注册函数"""
    event_type = getattr(event, 'post_type', None)
    
    # 从注册器获取所有函数
    functions = registry.get_functions()
    
    for func_info in functions:
        func_id = func_info['id']
        name = func_info['name']
        func = func_info['function']
        param_annotations = func_info['param_annotations']
        signature = func_info['signature']
        original_name = func_info['original_name']
        fun_arg_data = func_info.get('fun_arg_data')
        
        
        # 检查事件类型过滤
        if fun_arg_data and fun_arg_data.event_types and event_type and event_type not in fun_arg_data.event_types:
            continue
        
        # 检查参数类型匹配
        if not _is_event_matching(event, param_annotations):
            continue
        
        # 消息匹配逻辑
        msg_content = getattr(event, 'raw_message', '') if hasattr(event, 'raw_message') else ''
        
        # 使用 register_meta 中定义的 on_msg 函数
        on_msg_func = Messgaechat.on_message
        if fun_arg_data and fun_arg_data.on_msg:
            on_msg_func = fun_arg_data.on_msg
            
        match_result: chat_type = on_msg_func(name, msg_content)
        
        
        if match_result.type:
            
            # 构建参数字典
            call_kwargs = {}
            for param_name in signature.parameters:
                annotation = param_annotations.get(param_name)
                if (annotation and 
                    inspect.isclass(annotation) and 
                    issubclass(annotation, pydantic.BaseModel) and
                    _is_event_matching(event, {param_name: annotation})):
                    call_kwargs[param_name] = event
                elif param_name == 'commandargs' and hasattr(match_result, 'commandargs'):
                    call_kwargs[param_name] = match_result.commandargs
            
            try:
                block = fun_arg_data.block if fun_arg_data else False
                if block:
                    await func(**call_kwargs)
                    break
                else:
                    await func(**call_kwargs)
            except Exception as e:
                logger.error(f"调用函数 {name} (ID: {func_id}) 时出错: {e}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            pass