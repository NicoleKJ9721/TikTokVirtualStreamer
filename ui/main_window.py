#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window
主窗口

抖音虚拟主播GUI应用程序的主窗口
"""

import sys
import time
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QStatusBar, QMenuBar, QAction, QMessageBox, QSplitter,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFrame, QScrollArea, QCheckBox, QSpinBox,
    QComboBox, QSlider, QApplication
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QRect
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QLinearGradient, QBrush
)

try:
    from core.live_data_manager import LiveDataManager
except ImportError:
    # 如果导入失败，创建一个模拟的类
    from PyQt5.QtCore import QObject
    class LiveDataManager(QObject):
        message_received = pyqtSignal(dict)
        connection_status_changed = pyqtSignal(int)
        live_status_changed = pyqtSignal(int)
        error_occurred = pyqtSignal(str)
        statistics_updated = pyqtSignal(dict)
        
        def start_monitoring(self, url):
            return False
        
        def stop_monitoring(self):
            pass

from models.message_types import (
    MessageType, MessagePriority, ConnectionStatus, LiveStatus,
    get_message_display_name, get_message_color,
    get_connection_status_display_name, get_live_status_display_name
)

class LiveDataThread(QThread):
    """
    直播数据获取线程
    
    在后台获取直播数据，避免阻塞UI线程
    """
    
    # 信号定义
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._live_url = None
        self._is_running = False
        self._data_manager = None
    
    def set_live_url(self, live_url: str):
        """
        设置直播间URL
        
        Args:
            live_url: 直播间URL
        """
        self._live_url = live_url
    
    def run(self):
        """
        线程运行方法
        """
        try:
            if not self._live_url:
                self.error_occurred.emit("直播间URL不能为空")
                return
            
            self._is_running = True
            self.status_changed.emit("正在连接直播间...")
            
            # 创建数据管理器
            self._data_manager = LiveDataManager()
            
            # 连接信号
            self._data_manager.message_received.connect(self.data_received.emit)
            self._data_manager.error_occurred.connect(self.error_occurred.emit)
            
            # 开始监控
            if self._data_manager.start_monitoring(self._live_url):
                self.status_changed.emit("已连接到直播间")
                
                # 保持线程运行
                while self._is_running:
                    self.msleep(100)
            else:
                self.error_occurred.emit("连接直播间失败")
                
        except Exception as e:
            self.error_occurred.emit(f"线程运行错误: {str(e)}")
        finally:
            if self._data_manager:
                self._data_manager.stop_monitoring()
            self._is_running = False
            self.status_changed.emit("已断开连接")
    
    def stop_thread(self):
        """
        停止线程
        """
        self._is_running = False
        if self._data_manager:
            self._data_manager.stop_monitoring()
        self.quit()
        self.wait()

class MainWindow(QMainWindow):
    """
    主窗口类
    
    构建和管理整个应用程序的用户界面
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化状态
        self._is_monitoring = False
        self._live_thread = None
        self._message_count = 0
        self._statistics = {}
        
        # 初始化UI
        self._init_ui()
        self._init_connections()
        self._init_timers()
        
        # 设置初始状态
        self._update_connection_status(ConnectionStatus.DISCONNECTED)
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 设置窗口属性
        self.setWindowTitle("TikTok Virtual Streamer - 抖音虚拟主播数据监控")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建连接控制区域
        self._create_connection_control(main_layout)
        
        # 创建主要内容区域
        self._create_main_content(main_layout)
        
        # 创建状态栏
        self._create_status_bar()
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 应用样式
        self._apply_styles()
    
    def _create_connection_control(self, parent_layout):
        """
        创建连接控制区域
        
        Args:
            parent_layout: 父布局
        """
        # 连接控制组框
        connection_group = QGroupBox("连接控制")
        connection_group.setMaximumHeight(120)
        parent_layout.addWidget(connection_group)
        
        # 连接控制布局
        connection_layout = QGridLayout(connection_group)
        connection_layout.setSpacing(10)
        
        # 直播间URL输入
        url_label = QLabel("直播间地址:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入抖音直播间URL，例如: https://live.douyin.com/123456789")
        self.url_input.setMinimumHeight(35)
        
        # 连接按钮
        self.connect_button = QPushButton("开始监控")
        self.connect_button.setMinimumSize(120, 35)
        self.connect_button.setMaximumSize(120, 35)
        
        # 状态指示器
        status_label = QLabel("连接状态:")
        self.status_indicator = QLabel("未连接")
        self.status_indicator.setMinimumHeight(35)
        self.status_indicator.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
        """)
        
        # 添加到布局
        connection_layout.addWidget(url_label, 0, 0)
        connection_layout.addWidget(self.url_input, 0, 1, 1, 2)
        connection_layout.addWidget(self.connect_button, 0, 3)
        connection_layout.addWidget(status_label, 1, 0)
        connection_layout.addWidget(self.status_indicator, 1, 1)
        
        # 设置列拉伸
        connection_layout.setColumnStretch(1, 1)
    
    def _create_main_content(self, parent_layout):
        """
        创建主要内容区域
        
        Args:
            parent_layout: 父布局
        """
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        parent_layout.addWidget(splitter)
        
        # 创建左侧面板（消息显示）
        self._create_message_panel(splitter)
        
        # 创建右侧面板（统计信息）
        self._create_statistics_panel(splitter)
        
        # 设置分割器比例
        splitter.setSizes([800, 400])
    
    def _create_message_panel(self, parent):
        """
        创建消息显示面板
        
        Args:
            parent: 父控件
        """
        # 消息面板组框
        message_group = QGroupBox("实时消息")
        parent.addWidget(message_group)
        
        # 消息面板布局
        message_layout = QVBoxLayout(message_group)
        
        # 创建标签页
        self.message_tabs = QTabWidget()
        message_layout.addWidget(self.message_tabs)
        
        # 所有消息标签页
        self.all_messages_text = QTextEdit()
        self.all_messages_text.setReadOnly(True)
        self.all_messages_text.setMaximumBlockCount(1000)  # 限制最大行数
        self.message_tabs.addTab(self.all_messages_text, "所有消息")
        
        # 聊天消息标签页
        self.chat_messages_text = QTextEdit()
        self.chat_messages_text.setReadOnly(True)
        self.chat_messages_text.setMaximumBlockCount(500)
        self.message_tabs.addTab(self.chat_messages_text, "聊天消息")
        
        # 礼物消息标签页
        self.gift_messages_text = QTextEdit()
        self.gift_messages_text.setReadOnly(True)
        self.gift_messages_text.setMaximumBlockCount(500)
        self.message_tabs.addTab(self.gift_messages_text, "礼物消息")
        
        # 系统消息标签页
        self.system_messages_text = QTextEdit()
        self.system_messages_text.setReadOnly(True)
        self.system_messages_text.setMaximumBlockCount(500)
        self.message_tabs.addTab(self.system_messages_text, "系统消息")
    
    def _create_statistics_panel(self, parent):
        """
        创建统计信息面板
        
        Args:
            parent: 父控件
        """
        # 统计面板组框
        stats_group = QGroupBox("统计信息")
        parent.addWidget(stats_group)
        
        # 统计面板布局
        stats_layout = QVBoxLayout(stats_group)
        
        # 创建统计信息表格
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["项目", "数值"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setSelectionBehavior(QTableWidget.SelectRows)
        stats_layout.addWidget(self.stats_table)
        
        # 初始化统计表格
        self._init_statistics_table()
    
    def _init_statistics_table(self):
        """
        初始化统计信息表格
        """
        stats_items = [
            ("总消息数", "0"),
            ("聊天消息", "0"),
            ("礼物消息", "0"),
            ("点赞消息", "0"),
            ("进场消息", "0"),
            ("关注消息", "0"),
            ("运行时间", "00:00:00"),
            ("最后消息时间", "无")
        ]
        
        self.stats_table.setRowCount(len(stats_items))
        
        for row, (item, value) in enumerate(stats_items):
            self.stats_table.setItem(row, 0, QTableWidgetItem(item))
            self.stats_table.setItem(row, 1, QTableWidgetItem(value))
            
            # 设置第一列不可编辑
            self.stats_table.item(row, 0).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.stats_table.item(row, 1).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    
    def _create_status_bar(self):
        """
        创建状态栏
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加永久部件
        self.message_count_label = QLabel("消息数: 0")
        self.status_bar.addPermanentWidget(self.message_count_label)
        
        # 设置初始状态
        self.status_bar.showMessage("就绪")
    
    def _create_menu_bar(self):
        """
        创建菜单栏
        """
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 清空消息动作
        clear_action = QAction("清空消息", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self._clear_messages)
        file_menu.addAction(clear_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _init_connections(self):
        """
        初始化信号连接
        """
        # 连接按钮点击事件
        self.connect_button.clicked.connect(self._toggle_monitoring)
        
        # URL输入框回车事件
        self.url_input.returnPressed.connect(self._toggle_monitoring)
    
    def _init_timers(self):
        """
        初始化定时器
        """
        # 创建UI更新定时器
        self.ui_update_timer = QTimer()
        self.ui_update_timer.timeout.connect(self._update_ui)
        self.ui_update_timer.start(1000)  # 每秒更新一次
    
    def _apply_styles(self):
        """
        应用样式
        """
        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-family: "Consolas", "Monaco", monospace;
                font-size: 11px;
            }
            
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                padding: 5px 10px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
    
    def _toggle_monitoring(self):
        """
        切换监控状态
        """
        if not self._is_monitoring:
            self._start_monitoring()
        else:
            self._stop_monitoring()
    
    def _start_monitoring(self):
        """
        开始监控
        """
        live_url = self.url_input.text().strip()
        
        if not live_url:
            QMessageBox.warning(self, "警告", "请输入直播间地址")
            return
        
        try:
            # 创建并启动线程
            self._live_thread = LiveDataThread()
            self._live_thread.set_live_url(live_url)
            
            # 连接信号
            self._live_thread.data_received.connect(self._on_message_received)
            self._live_thread.error_occurred.connect(self._on_error_occurred)
            self._live_thread.status_changed.connect(self._on_status_changed)
            
            # 启动线程
            self._live_thread.start()
            
            # 更新UI状态
            self._is_monitoring = True
            self.connect_button.setText("停止监控")
            self.connect_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """)
            self.url_input.setEnabled(False)
            
            self.status_bar.showMessage(f"正在监控: {live_url}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动监控失败: {str(e)}")
    
    def _stop_monitoring(self):
        """
        停止监控
        """
        try:
            # 停止线程
            if self._live_thread:
                self._live_thread.stop_thread()
                self._live_thread = None
            
            # 更新UI状态
            self._is_monitoring = False
            self.connect_button.setText("开始监控")
            self.connect_button.setStyleSheet("")  # 恢复默认样式
            self.url_input.setEnabled(True)
            
            self._update_connection_status(ConnectionStatus.DISCONNECTED)
            self.status_bar.showMessage("监控已停止")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"停止监控失败: {str(e)}")
    
    def _on_message_received(self, message_data: Dict[str, Any]):
        """
        处理收到的消息
        
        Args:
            message_data: 消息数据
        """
        try:
            # 更新消息计数
            self._message_count += 1
            self.message_count_label.setText(f"消息数: {self._message_count}")
            
            # 格式化消息
            formatted_message = self._format_message(message_data)
            
            # 添加到所有消息
            self.all_messages_text.append(formatted_message)
            
            # 根据消息类型添加到对应标签页
            message_type = message_data.get('type', MessageType.UNKNOWN)
            
            if message_type == MessageType.CHAT:
                self.chat_messages_text.append(formatted_message)
            elif message_type == MessageType.GIFT:
                self.gift_messages_text.append(formatted_message)
            elif message_type in [MessageType.SYSTEM, MessageType.LIVE_STATUS]:
                self.system_messages_text.append(formatted_message)
            
        except Exception as e:
            self.status_bar.showMessage(f"处理消息错误: {str(e)}")
    
    def _format_message(self, message_data: Dict[str, Any]) -> str:
        """
        格式化消息
        
        Args:
            message_data: 消息数据
            
        Returns:
            str: 格式化后的消息
        """
        try:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            message_type = message_data.get('type', MessageType.UNKNOWN)
            type_name = get_message_display_name(message_type)
            
            # 基础信息
            formatted = f"[{timestamp}] [{type_name}] "
            
            # 根据消息类型添加具体内容
            if message_type == MessageType.CHAT:
                user = message_data.get('user', '未知用户')
                content = message_data.get('content', '')
                formatted += f"{user}: {content}"
            
            elif message_type == MessageType.GIFT:
                user = message_data.get('user', '未知用户')
                gift_name = message_data.get('gift_name', '未知礼物')
                count = message_data.get('count', 1)
                formatted += f"{user} 送出 {gift_name} x{count}"
            
            elif message_type == MessageType.LIKE:
                user = message_data.get('user', '未知用户')
                count = message_data.get('count', 1)
                formatted += f"{user} 点赞 x{count}"
            
            elif message_type == MessageType.ENTER:
                user = message_data.get('user', '未知用户')
                formatted += f"{user} 进入直播间"
            
            elif message_type == MessageType.FOLLOW:
                user = message_data.get('user', '未知用户')
                formatted += f"{user} 关注了主播"
            
            else:
                # 其他类型消息
                content = message_data.get('content', str(message_data))
                formatted += content
            
            return formatted
            
        except Exception as e:
            return f"[{time.strftime('%H:%M:%S')}] [错误] 消息格式化失败: {str(e)}"
    
    def _on_error_occurred(self, error_message: str):
        """
        处理错误
        
        Args:
            error_message: 错误消息
        """
        self.status_bar.showMessage(f"错误: {error_message}")
        
        # 添加错误消息到系统消息
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        error_text = f"[{timestamp}] [错误] {error_message}"
        self.system_messages_text.append(error_text)
    
    def _on_status_changed(self, status_message: str):
        """
        处理状态变化
        
        Args:
            status_message: 状态消息
        """
        self.status_bar.showMessage(status_message)
    
    def _update_connection_status(self, status: ConnectionStatus):
        """
        更新连接状态显示
        
        Args:
            status: 连接状态
        """
        status_text = get_connection_status_display_name(status)
        self.status_indicator.setText(status_text)
        
        # 设置状态指示器颜色
        if status == ConnectionStatus.CONNECTED:
            color = "#4CAF50"  # 绿色
        elif status == ConnectionStatus.CONNECTING:
            color = "#FF9800"  # 橙色
        elif status == ConnectionStatus.ERROR:
            color = "#f44336"  # 红色
        else:
            color = "#9E9E9E"  # 灰色
        
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border: 1px solid {color};
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }}
        """)
    
    def _update_statistics(self, statistics: Dict[str, Any]):
        """
        更新统计信息
        
        Args:
            statistics: 统计数据
        """
        try:
            # 更新统计表格
            stats_mapping = {
                0: str(statistics.get('total_messages', 0)),
                1: str(statistics.get('chat_messages', 0)),
                2: str(statistics.get('gift_messages', 0)),
                3: str(statistics.get('like_messages', 0)),
                4: str(statistics.get('enter_messages', 0)),
                5: str(statistics.get('follow_messages', 0)),
            }
            
            # 运行时间
            running_time = statistics.get('running_time', 0)
            hours = int(running_time // 3600)
            minutes = int((running_time % 3600) // 60)
            seconds = int(running_time % 60)
            stats_mapping[6] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # 最后消息时间
            last_message_time = statistics.get('last_message_time')
            if last_message_time:
                stats_mapping[7] = time.strftime("%H:%M:%S", time.localtime(last_message_time))
            else:
                stats_mapping[7] = "无"
            
            # 更新表格
            for row, value in stats_mapping.items():
                if row < self.stats_table.rowCount():
                    self.stats_table.setItem(row, 1, QTableWidgetItem(value))
            
        except Exception as e:
            self.status_bar.showMessage(f"更新统计信息错误: {str(e)}")
    
    def _update_ui(self):
        """
        定期更新UI
        """
        # 这里可以添加定期更新的逻辑
        pass
    
    def _clear_messages(self):
        """
        清空所有消息
        """
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有消息吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.all_messages_text.clear()
            self.chat_messages_text.clear()
            self.gift_messages_text.clear()
            self.system_messages_text.clear()
            
            self._message_count = 0
            self.message_count_label.setText("消息数: 0")
            
            self.status_bar.showMessage("消息已清空")
    
    def _show_about(self):
        """
        显示关于对话框
        """
        QMessageBox.about(
            self, "关于",
            "TikTok Virtual Streamer v1.0.0\n\n"
            "抖音虚拟主播数据监控工具\n\n"
            "功能特性:\n"
            "• 实时监控直播间消息\n"
            "• 支持多种消息类型解析\n"
            "• 提供详细的统计信息\n"
            "• 现代化的用户界面\n\n"
            "技术栈: Python, PyQt5, WebSocket\n\n"
            "© 2024 TikTok Virtual Streamer Team"
        )
    
    def closeEvent(self, event):
        """
        窗口关闭事件
        
        Args:
            event: 关闭事件
        """
        if self._is_monitoring:
            reply = QMessageBox.question(
                self, "确认退出", "正在监控中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            # 停止监控
            self._stop_monitoring()
        
        # 清理资源
        if self.ui_update_timer:
            self.ui_update_timer.stop()
        
        event.accept()