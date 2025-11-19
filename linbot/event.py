import pydantic

class fix_event(pydantic.BaseModel):
    class Config:
        extra = "allow"
    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)

class base_event(pydantic.BaseModel):
    time: int = None
    """时间戳"""
    self_id: int = None
    """机器人QQ号"""
    post_type: str = None
    """上报类型，message：消息上报，notice：通知上报，request"""

    class Config:
        extra = "allow"

    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)

class SendReturn(base_event):
    status: str
    """发送状态"""
    retcode: int
    """返回码"""
    data: dict
    """返回数据"""

    class Config:
        extra = "allow"
    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)

class Sender(pydantic.BaseModel):
    """发送者"""
    user_id: int
    """发送者QQ号"""
    nickname: str
    """发送者昵称"""
    card: str
    """发送者名片"""
    role: str = None
    """发送者角色"""
    title: str = None
    """发送者头衔"""
    group_id: int = None
    """临时会话群号"""

    class Config:
        extra = "allow"
    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)

class Message(pydantic.BaseModel):
    """消息内容"""
    type: str
    """消息类型"""
    data: dict
    """消息数据"""

    class Config:
        extra = "allow"
    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)

class MessageEvent(base_event):
    """消息事件"""
    user_id: int
    """发送者QQ号"""
    message_id: int
    """消息ID"""
    message_seq: int
    """消息序号"""
    message_type: str
    """消息类型"""
    sender: Sender
    """发送者"""
    raw_message: str
    """原始消息内容"""
    font: int
    """字体"""
    sub_type: str
    """消息子类型"""
    message : Message
    """消息内容"""
    message_format : str
    """消息内容格式"""
    post_type : str
    """上报类型"""
    raw_pb : str

    class Config:
        extra = "allow"
    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)

class GroupMessageEvent(MessageEvent):
    """群消息事件"""
    group_id: int
    """群号"""
    group_name: str
    """群名称"""
    target_id: int
    """目标ID"""

    class Config:
        extra = "allow"

    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)

class PrivateMessageEvent(MessageEvent):
    """私聊消息事件"""
    target_id: int
    """目标ID"""

    class Config:
        extra = "allow"

    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in data.items():
            if isinstance(field_value, dict):
                setattr(self, field_name, fix_event(**field_value))
            else:
                setattr(self, field_name, field_value)



{"self_id":3558183277,"user_id":3558183277,"time":1763487944,"message_id":60065708,"message_seq":12733,"message_type":"group","sender":{"user_id":3558183277,"nickname":"霖bot","card":"","role":"member","title":""},"raw_message":"1","font":14,"sub_type":"normal","message":[{"type":"text","data":{"text":"1"}}],"message_format":"array","post_type":"message_sent","raw_pb":"","group_id":632916902,"group_name":"机器人数据中转群","target_id":632916902}
{"self_id":3558183277,"user_id":3558183277,"time":1763488544,"message_id":143851010,"message_seq":145,"message_type":"private","sender":{"user_id":3558183277,"nickname":"霖bot","card":""},"raw_message":"2","font":14,"sub_type":"friend","message":[{"type":"text","data":{"text":"2"}}],"message_format":"array","post_type":"message_sent","raw_pb":"","target_id":3549337307}