import pydantic
import re

class chat_type(pydantic.BaseModel):
    type:bool = False
    "消息是否匹配规则"
    commandargs:str = None
    "除指令外剩余的参数，适用于指令+参数的情况"


class Messgaechat:
    @staticmethod
    def on_message(*args, **kwargs):
        return chat_type(type=True)
    
    @staticmethod
    def on_command(instruction: str=None, msg:str=None):
        if instruction is not None and msg is not None:
            if res:= re.match(rf"^{instruction}(.*)", msg):
                arg = res.groups()[0]
                if len(arg) == 0:
                    arg = " "
                return chat_type(type=True, commandargs=arg)
        return chat_type(type=False)