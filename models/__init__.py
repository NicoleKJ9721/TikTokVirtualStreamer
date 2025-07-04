#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Models module for TikTok Virtual Streamer
抖音虚拟主播模型模块
"""

__version__ = "1.0.0"
__author__ = "TikTok Virtual Streamer Team"

from .message_types import (
    MessageType, MessagePriority, ConnectionStatus, LiveStatus,
    get_message_display_name, get_message_priority, get_message_color
)

__all__ = [
    'MessageType',
    'MessagePriority', 
    'ConnectionStatus',
    'LiveStatus',
    'get_message_display_name',
    'get_message_priority',
    'get_message_color'
]