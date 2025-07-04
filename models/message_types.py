#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Message Types Definition
消息类型定义

定义直播间各种消息类型、优先级、连接状态等枚举
"""

from enum import Enum, IntEnum
from typing import Dict, Tuple

class MessageType(IntEnum):
    """
    消息类型枚举
    """
    UNKNOWN = 0          # 未知消息
    CHAT = 1            # 聊天消息
    GIFT = 2            # 礼物消息
    LIKE = 3            # 点赞消息
    ENTER = 4           # 进场消息
    FOLLOW = 5          # 关注消息
    STATS = 6           # 统计消息
    FANSCLUB = 7        # 粉丝团消息
    LIVE_STATUS = 8     # 直播状态消息
    EMOJI = 9           # 表情包消息
    RANKING = 10        # 排行榜消息
    ROOM_USER_SEQ = 11  # 房间用户序列消息
    SOCIAL = 12         # 社交消息
    CONTROL = 13        # 控制消息
    SYSTEM = 14         # 系统消息

class MessagePriority(IntEnum):
    """
    消息优先级枚举
    """
    LOW = 1         # 低优先级
    NORMAL = 2      # 普通优先级
    HIGH = 3        # 高优先级
    CRITICAL = 4    # 关键优先级

class ConnectionStatus(IntEnum):
    """
    连接状态枚举
    """
    DISCONNECTED = 0    # 未连接
    CONNECTING = 1      # 连接中
    CONNECTED = 2       # 已连接
    RECONNECTING = 3    # 重连中
    ERROR = 4          # 连接错误

class LiveStatus(IntEnum):
    """
    直播状态枚举
    """
    UNKNOWN = 0     # 未知状态
    OFFLINE = 1     # 未开播
    LIVE = 2        # 直播中
    PAUSE = 3       # 暂停
    END = 4         # 已结束
    REPLAY = 5      # 回放中

# 消息类型显示名称映射
MESSAGE_TYPE_DISPLAY_NAMES: Dict[MessageType, str] = {
    MessageType.UNKNOWN: "未知消息",
    MessageType.CHAT: "聊天消息",
    MessageType.GIFT: "礼物消息",
    MessageType.LIKE: "点赞消息",
    MessageType.ENTER: "进场消息",
    MessageType.FOLLOW: "关注消息",
    MessageType.STATS: "统计消息",
    MessageType.FANSCLUB: "粉丝团消息",
    MessageType.LIVE_STATUS: "直播状态",
    MessageType.EMOJI: "表情包消息",
    MessageType.RANKING: "排行榜消息",
    MessageType.ROOM_USER_SEQ: "用户序列消息",
    MessageType.SOCIAL: "社交消息",
    MessageType.CONTROL: "控制消息",
    MessageType.SYSTEM: "系统消息"
}

# 消息类型优先级映射
MESSAGE_TYPE_PRIORITIES: Dict[MessageType, MessagePriority] = {
    MessageType.UNKNOWN: MessagePriority.LOW,
    MessageType.CHAT: MessagePriority.NORMAL,
    MessageType.GIFT: MessagePriority.HIGH,
    MessageType.LIKE: MessagePriority.LOW,
    MessageType.ENTER: MessagePriority.NORMAL,
    MessageType.FOLLOW: MessagePriority.HIGH,
    MessageType.STATS: MessagePriority.LOW,
    MessageType.FANSCLUB: MessagePriority.NORMAL,
    MessageType.LIVE_STATUS: MessagePriority.CRITICAL,
    MessageType.EMOJI: MessagePriority.NORMAL,
    MessageType.RANKING: MessagePriority.LOW,
    MessageType.ROOM_USER_SEQ: MessagePriority.LOW,
    MessageType.SOCIAL: MessagePriority.NORMAL,
    MessageType.CONTROL: MessagePriority.CRITICAL,
    MessageType.SYSTEM: MessagePriority.HIGH
}

# 消息类型颜色映射 (RGB格式)
MESSAGE_TYPE_COLORS: Dict[MessageType, Tuple[int, int, int]] = {
    MessageType.UNKNOWN: (128, 128, 128),      # 灰色
    MessageType.CHAT: (0, 0, 0),              # 黑色
    MessageType.GIFT: (255, 0, 0),            # 红色
    MessageType.LIKE: (255, 192, 203),        # 粉色
    MessageType.ENTER: (0, 128, 0),           # 绿色
    MessageType.FOLLOW: (255, 165, 0),        # 橙色
    MessageType.STATS: (128, 128, 128),       # 灰色
    MessageType.FANSCLUB: (138, 43, 226),     # 紫色
    MessageType.LIVE_STATUS: (255, 0, 0),     # 红色
    MessageType.EMOJI: (255, 255, 0),         # 黄色
    MessageType.RANKING: (0, 0, 255),         # 蓝色
    MessageType.ROOM_USER_SEQ: (128, 128, 128), # 灰色
    MessageType.SOCIAL: (0, 191, 255),        # 深天蓝色
    MessageType.CONTROL: (255, 0, 0),         # 红色
    MessageType.SYSTEM: (255, 140, 0)         # 深橙色
}

# 连接状态显示名称映射
CONNECTION_STATUS_DISPLAY_NAMES: Dict[ConnectionStatus, str] = {
    ConnectionStatus.DISCONNECTED: "未连接",
    ConnectionStatus.CONNECTING: "连接中",
    ConnectionStatus.CONNECTED: "已连接",
    ConnectionStatus.RECONNECTING: "重连中",
    ConnectionStatus.ERROR: "连接错误"
}

# 直播状态显示名称映射
LIVE_STATUS_DISPLAY_NAMES: Dict[LiveStatus, str] = {
    LiveStatus.UNKNOWN: "未知状态",
    LiveStatus.OFFLINE: "未开播",
    LiveStatus.LIVE: "直播中",
    LiveStatus.PAUSE: "暂停",
    LiveStatus.END: "已结束",
    LiveStatus.REPLAY: "回放中"
}

def get_message_display_name(message_type: MessageType) -> str:
    """
    获取消息类型的显示名称
    
    Args:
        message_type: 消息类型
        
    Returns:
        str: 显示名称
    """
    return MESSAGE_TYPE_DISPLAY_NAMES.get(message_type, "未知消息")

def get_message_priority(message_type: MessageType) -> MessagePriority:
    """
    获取消息类型的优先级
    
    Args:
        message_type: 消息类型
        
    Returns:
        MessagePriority: 消息优先级
    """
    return MESSAGE_TYPE_PRIORITIES.get(message_type, MessagePriority.LOW)

def get_message_color(message_type: MessageType) -> Tuple[int, int, int]:
    """
    获取消息类型的颜色
    
    Args:
        message_type: 消息类型
        
    Returns:
        Tuple[int, int, int]: RGB颜色值
    """
    return MESSAGE_TYPE_COLORS.get(message_type, (0, 0, 0))

def get_connection_status_display_name(status: ConnectionStatus) -> str:
    """
    获取连接状态的显示名称
    
    Args:
        status: 连接状态
        
    Returns:
        str: 显示名称
    """
    return CONNECTION_STATUS_DISPLAY_NAMES.get(status, "未知状态")

def get_live_status_display_name(status: LiveStatus) -> str:
    """
    获取直播状态的显示名称
    
    Args:
        status: 直播状态
        
    Returns:
        str: 显示名称
    """
    return LIVE_STATUS_DISPLAY_NAMES.get(status, "未知状态")