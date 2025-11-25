# main/registry.py
import uuid
import inspect
from typing import Dict, List, Callable, Any, Optional
from logger import Logging

logger = Logging.logger

class FunctionRegistry:
    def __init__(self):
        self._functions: Dict[str, Dict] = {}
        self._plugin_functions: Dict[str, List[str]] = {}
    
    def register(self, func: Callable, name: str = None, plugin_name: str = "unknown", 
                 fun_arg_data: Any = None) -> str:
        """注册函数并返回唯一ID"""
        func_id = str(uuid.uuid4())
        
        # 获取函数信息
        signature = inspect.signature(func)
        param_annotations = {}
        
        for param_name, param in signature.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                param_annotations[param_name] = param.annotation
            else:
                param_annotations[param_name] = None
        
        # 存储函数信息
        self._functions[func_id] = {
            'id': func_id,
            'name': name or func.__name__,
            'function': func,
            'param_annotations': param_annotations,
            'signature': signature,
            'original_name': func.__name__,
            'plugin': plugin_name,
            'fun_arg_data': fun_arg_data  # 存储 register_meta 实例
        }
        
        # 记录插件与函数的关联
        if plugin_name not in self._plugin_functions:
            self._plugin_functions[plugin_name] = []
        self._plugin_functions[plugin_name].append(func_id)

        return func_id
    
    def unregister(self, func_id: str):
        """注销函数"""
        if func_id in self._functions:
            func_info = self._functions[func_id]
            plugin_name = func_info['plugin']
            
            # 从插件关联中移除
            if plugin_name in self._plugin_functions and func_id in self._plugin_functions[plugin_name]:
                self._plugin_functions[plugin_name].remove(func_id)
            
            # 从函数列表中移除
            del self._functions[func_id]
    
    def unregister_plugin(self, plugin_name: str):
        """注销插件的所有函数"""
        if plugin_name in self._plugin_functions:
            for func_id in self._plugin_functions[plugin_name][:]:
                self.unregister(func_id)
    
    def get_functions(self) -> List[Dict]:
        """获取所有函数信息"""
        return list(self._functions.values())
    
    def get_plugin_functions(self, plugin_name: str) -> List[Dict]:
        """获取指定插件的函数"""
        if plugin_name not in self._plugin_functions:
            return []
        
        return [self._functions[func_id] for func_id in self._plugin_functions[plugin_name] 
                if func_id in self._functions]
    
    def clear(self):
        """清空所有注册的函数"""
        self._functions.clear()
        self._plugin_functions.clear()

# 全局注册器实例
registry = FunctionRegistry()