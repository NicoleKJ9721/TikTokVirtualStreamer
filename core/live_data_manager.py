#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Data Manager
直播数据管理器

负责管理直播数据的获取、处理和分发
"""

import time
import threading
from typing import Optional, Dict, Any, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication

try:
    from .douyin_live_fetcher import DouyinLiveWebFetcher
except ImportError:
    # 如果导入失败，创建一个模拟的类
    class DouyinLiveWebFetcher:
        def __init__(self, *args, **kwargs):
            pass
        
        def start(self):
            pass
        
        def stop(self):
            pass

from models.message_types import (
    MessageType, MessagePriority, ConnectionStatus, LiveStatus
)

class LiveDataManager(QObject):
    """
    直播数据管理器
    
    封装DouyinLiveWebFetcher功能，适配PyQt5信号系统
    """
    
    # 信号定义
    message_received = pyqtSignal(dict)  # 收到消息
    connection_status_changed = pyqtSignal(int)  # 连接状态变化
    live_status_changed = pyqtSignal(int)  # 直播状态变化
    error_occurred = pyqtSignal(str)  # 发生错误
    statistics_updated = pyqtSignal(dict)  # 统计信息更新
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化状态
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._live_status = LiveStatus.UNKNOWN
        self._is_running = False
        self._room_id = None
        self._live_url = None
        
        # 统计信息
        self._statistics = {
            'total_messages': 0,
            'chat_messages': 0,
            'gift_messages': 0,
            'like_messages': 0,
            'enter_messages': 0,
            'follow_messages': 0,
            'start_time': None,
            'last_message_time': None
        }
        
        # 消息处理器映射
        self._message_handlers = {
            MessageType.CHAT: self._handle_chat_message,
            MessageType.GIFT: self._handle_gift_message,
            MessageType.LIKE: self._handle_like_message,
            MessageType.ENTER: self._handle_enter_message,
            MessageType.FOLLOW: self._handle_follow_message,
            MessageType.STATS: self._handle_stats_message,
            MessageType.FANSCLUB: self._handle_fansclub_message,
            MessageType.LIVE_STATUS: self._handle_live_status_message,
            MessageType.EMOJI: self._handle_emoji_message,
            MessageType.RANKING: self._handle_ranking_message
        }
        
        # 初始化抖音直播获取器
        self._fetcher = None
        
        # 监控定时器
        self._monitor_timer = QTimer()
        self._monitor_timer.timeout.connect(self._monitor_loop)
        
        # 统计重置定时器
        self._stats_reset_timer = QTimer()
        self._stats_reset_timer.timeout.connect(self._reset_statistics)
    
    @property
    def connection_status(self) -> ConnectionStatus:
        """获取连接状态"""
        return self._connection_status
    
    @property
    def live_status(self) -> LiveStatus:
        """获取直播状态"""
        return self._live_status
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._is_running
    
    @property
    def room_id(self) -> Optional[str]:
        """获取房间ID"""
        return self._room_id
    
    @property
    def statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self._statistics.copy()
    
    def start_monitoring(self, live_url: str) -> bool:
        """
        开始监控直播间
        
        Args:
            live_url: 直播间URL
            
        Returns:
            bool: 是否成功开始监控
        """
        try:
            if self._is_running:
                self.stop_monitoring()
            
            self._live_url = live_url
            self._room_id = self._extract_room_id(live_url)
            
            # 重置统计信息
            self._reset_statistics()
            self._statistics['start_time'] = time.time()
            
            # 创建并配置抖音直播获取器
            self._fetcher = DouyinLiveWebFetcher(
                live_url=live_url,
                on_message=self._on_message_received,
                on_error=self._on_error_occurred,
                on_connection_change=self._on_connection_changed
            )
            
            # 启动获取器
            self._fetcher.start()
            
            # 更新状态
            self._is_running = True
            self._set_connection_status(ConnectionStatus.CONNECTING)
            
            # 启动监控定时器
            self._monitor_timer.start(1000)  # 每秒检查一次
            
            # 启动统计重置定时器（每小时重置一次）
            self._stats_reset_timer.start(3600000)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"启动监控失败: {str(e)}")
            return False
    
    def stop_monitoring(self):
        """
        停止监控直播间
        """
        try:
            self._is_running = False
            
            # 停止定时器
            self._monitor_timer.stop()
            self._stats_reset_timer.stop()
            
            # 停止获取器
            if self._fetcher:
                self._fetcher.stop()
                self._fetcher = None
            
            # 更新状态
            self._set_connection_status(ConnectionStatus.DISCONNECTED)
            self._set_live_status(LiveStatus.UNKNOWN)
            
        except Exception as e:
            self.error_occurred.emit(f"停止监控失败: {str(e)}")
    
    def _extract_room_id(self, live_url: str) -> Optional[str]:
        """
        从直播URL中提取房间ID
        
        Args:
            live_url: 直播间URL
            
        Returns:
            Optional[str]: 房间ID
        """
        try:
            # 简单的房间ID提取逻辑
            if 'live.douyin.com' in live_url:
                parts = live_url.split('/')
                for part in parts:
                    if part.isdigit():
                        return part
            return None
        except Exception:
            return None
    
    def _set_connection_status(self, status: ConnectionStatus):
        """
        设置连接状态
        
        Args:
            status: 连接状态
        """
        if self._connection_status != status:
            self._connection_status = status
            self.connection_status_changed.emit(status.value)
    
    def _set_live_status(self, status: LiveStatus):
        """
        设置直播状态
        
        Args:
            status: 直播状态
        """
        if self._live_status != status:
            self._live_status = status
            self.live_status_changed.emit(status.value)
    
    def _on_message_received(self, message_data: Dict[str, Any]):
        """
        处理收到的消息
        
        Args:
            message_data: 消息数据
        """
        try:
            # 更新统计信息
            self._statistics['total_messages'] += 1
            self._statistics['last_message_time'] = time.time()
            
            # 获取消息类型
            message_type = message_data.get('type', MessageType.UNKNOWN)
            
            # 调用对应的处理器
            handler = self._message_handlers.get(message_type)
            if handler:
                enhanced_message = handler(message_data)
            else:
                enhanced_message = self._handle_unknown_message(message_data)
            
            # 发射信号
            self.message_received.emit(enhanced_message)
            
            # 更新统计信息
            self.statistics_updated.emit(self._statistics)
            
        except Exception as e:
            self.error_occurred.emit(f"处理消息失败: {str(e)}")
    
    def _on_error_occurred(self, error_message: str):
        """
        处理错误
        
        Args:
            error_message: 错误消息
        """
        self.error_occurred.emit(error_message)
    
    def _on_connection_changed(self, is_connected: bool):
        """
        处理连接状态变化
        
        Args:
            is_connected: 是否已连接
        """
        if is_connected:
            self._set_connection_status(ConnectionStatus.CONNECTED)
        else:
            self._set_connection_status(ConnectionStatus.DISCONNECTED)
    
    def _handle_chat_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理聊天消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        self._statistics['chat_messages'] += 1
        
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.NORMAL,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_gift_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理礼物消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        self._statistics['gift_messages'] += 1
        
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.HIGH,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_like_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理点赞消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        self._statistics['like_messages'] += 1
        
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.LOW,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_enter_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理进场消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        self._statistics['enter_messages'] += 1
        
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.NORMAL,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_follow_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理关注消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        self._statistics['follow_messages'] += 1
        
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.HIGH,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_stats_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理统计消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.LOW,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_fansclub_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理粉丝团消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.NORMAL,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_live_status_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理直播状态消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        # 更新直播状态
        status = message_data.get('status', LiveStatus.UNKNOWN)
        if isinstance(status, int):
            try:
                status = LiveStatus(status)
            except ValueError:
                status = LiveStatus.UNKNOWN
        
        self._set_live_status(status)
        
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.CRITICAL,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_emoji_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理表情包消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.NORMAL,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_ranking_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理排行榜消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.LOW,
            'timestamp': time.time(),
            'processed': True
        })
        
        return enhanced_message
    
    def _handle_unknown_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理未知类型消息
        
        Args:
            message_data: 原始消息数据
            
        Returns:
            Dict[str, Any]: 增强的消息数据
        """
        enhanced_message = message_data.copy()
        enhanced_message.update({
            'priority': MessagePriority.LOW,
            'timestamp': time.time(),
            'processed': True,
            'unknown': True
        })
        
        return enhanced_message
    
    def _monitor_loop(self):
        """
        监控循环
        
        定期检查连接状态和统计信息
        """
        try:
            # 检查连接状态
            if self._fetcher and self._is_running:
                # 这里可以添加更多的监控逻辑
                pass
            
            # 更新统计信息
            current_time = time.time()
            if self._statistics['start_time']:
                self._statistics['running_time'] = current_time - self._statistics['start_time']
            
            # 发射统计信息更新信号
            self.statistics_updated.emit(self._statistics)
            
        except Exception as e:
            self.error_occurred.emit(f"监控循环错误: {str(e)}")
    
    def _reset_statistics(self):
        """
        重置统计信息
        """
        start_time = self._statistics.get('start_time')
        self._statistics = {
            'total_messages': 0,
            'chat_messages': 0,
            'gift_messages': 0,
            'like_messages': 0,
            'enter_messages': 0,
            'follow_messages': 0,
            'start_time': start_time,
            'last_message_time': None,
            'running_time': 0
        }
        
        self.statistics_updated.emit(self._statistics)