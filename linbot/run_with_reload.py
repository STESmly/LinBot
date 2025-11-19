import os
import sys
import time
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logger import Logging

logger = Logging.logger

class PythonFileChangeHandler(FileSystemEventHandler):
    def __init__(self, script_path, debounce_interval=1.0):
        self.script_path = script_path
        self.debounce_interval = debounce_interval
        self.timer = None
        self.last_modified = {}
        self.process = None
        self.start_script()
        
    def on_modified(self, event):
        """
        当监视的文件被修改时触发的事件处理函数
        实现了防抖功能，避免短时间内多次触发重启
        """
        # 只处理.py文件且不是目录
        if event.src_path.endswith('.py') and not event.is_directory:
            # 获取文件当前的修改时间
            current_mtime = os.path.getmtime(event.src_path)
            
            # 检查这个文件是否在防抖间隔内已经触发过
            if event.src_path in self.last_modified:
                time_since_last = current_mtime - self.last_modified[event.src_path]
                if time_since_last < self.debounce_interval:
                    # 在防抖间隔内，忽略这次触发
                    return
            
            # 更新最后修改时间
            self.last_modified[event.src_path] = current_mtime
            
            # 取消之前的定时器（如果存在）
            if self.timer is not None:
                self.timer.cancel()
            
            # 设置新的定时器
            self.timer = threading.Timer(self.debounce_interval, self._delayed_restart, [event.src_path])
            self.timer.start()
    
    def _delayed_restart(self, file_path):
        """延迟重启，确保文件修改完成"""
        logger.debug(f"检测到文件变更: {os.path.basename(file_path)}")
        logger.info("正在重新启动...")
        self.restart_script()
    
    def restart_script(self):
        self.start_script()
    
    def start_script(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)  # 等待5秒让进程正常退出
            except subprocess.TimeoutExpired:
                logger.error("进程未正常退出，强制终止...")
                self.process.kill()
                self.process.wait()
        
        logger.info("启动脚本...")
        self.process = subprocess.Popen([sys.executable, self.script_path])
    
    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
        if self.process:
            self.process.terminate()
            self.process.wait()

def main():
    script_to_run = "wsclient.py"
    
    if not os.path.exists(script_to_run):
        logger.error(f"错误: 找不到 {script_to_run}")
        return
    
    logger.debug(f"正在监视 Python 文件变化，自动重载 {script_to_run}")
    
    # 设置防抖时间为1秒
    event_handler = PythonFileChangeHandler(script_to_run, debounce_interval=1.0)
    observer = Observer()
    
    # 监视当前目录及其所有子目录
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止监视器...")
        observer.stop()
        event_handler.stop()
    
    observer.join()

if __name__ == "__main__":
    main()