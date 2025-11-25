# main/plugins_manager.py
import os,asyncio
import importlib
import inspect
import sys
from typing import Dict, List, Any
from logger import Logging
from registry import registry
from chat import set_current_plugin_name, clear_current_plugin_name

logger = Logging.logger

class PluginManager:
    def __init__(self):
        self.plugins = {}
        
    def load_plugins(self, plugins_base_dir: str):
        """加载所有插件"""
        if not os.path.exists(plugins_base_dir):
            logger.error(f"插件目录不存在: {plugins_base_dir}")
            return
            
        plugin_count = 0
        
        # 1. 加载根目录的 __init__.py
        root_plugin_path = os.path.join(plugins_base_dir, "__init__.py")
        if os.path.exists(root_plugin_path):
            try:
                self._load_single_plugin("__root__", plugins_base_dir, root_plugin_path)
                logger.success(f"加载根目录插件成功")
                plugin_count += 1
            except Exception as e:
                logger.error(f"加载根目录插件失败: {e}")
        
        # 2. 加载所有子目录中的插件
        for item_name in os.listdir(plugins_base_dir):
            item_path = os.path.join(plugins_base_dir, item_name)
            if os.path.isdir(item_path):
                plugin_init_file = os.path.join(item_path, "__init__.py")
                if os.path.exists(plugin_init_file):
                    try:
                        self._load_single_plugin(item_name, item_path, plugin_init_file)
                        logger.success(f"加载插件 {item_name} 成功")
                        plugin_count += 1
                    except Exception as e:
                        logger.error(f"加载插件 {item_name} 失败: {e}")
        
        # 获取注册的函数统计
        functions = registry.get_functions()
        
        logger.debug(f"插件加载完成，共加载 {plugin_count} 个插件")
        logger.debug(f"注册的函数处理器数量: {len(functions)}")
    
    def _load_single_plugin(self, plugin_name: str, plugin_path: str, plugin_file: str):
        """加载单个插件"""
        original_sys_path = sys.path.copy()
        
        try:
            if plugin_path not in sys.path:
                sys.path.insert(0, plugin_path)
            
            # 设置当前插件名称，这样装饰器就能知道当前正在加载的插件
            set_current_plugin_name(plugin_name)
            
            # 动态导入插件
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            module.__package__ = plugin_name
            spec.loader.exec_module(module)
            
            # 注册处理器
            self._register_handlers(module, plugin_name)
            self.plugins[plugin_name] = module
            
        except Exception as e:
            logger.error(f"导入插件 {plugin_name} 时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        finally:
            # 清除当前插件名称
            clear_current_plugin_name()
            sys.path[:] = original_sys_path
    
    def _register_handlers(self, module, plugin_name: str):
        """注册模块中的所有处理器"""

        fun_call_count = 0
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, '_fun_call_register_meta'):
                fun_call_count += 1
    
    async def handle_event(self, event_type: str, event_data: Any):
        """处理事件"""
        try:
            from chat import fun_call
            await fun_call(event_data)
        except Exception as e:
            logger.error(f"调用 fun_call 时出错: {e}")

# 全局插件管理器实例
plugin_manager = PluginManager()