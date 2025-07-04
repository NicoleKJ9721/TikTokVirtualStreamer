#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Virtual Streamer GUI Application
抖音虚拟主播GUI应用程序主入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖模块都已正确安装")
    sys.exit(1)

def check_dependencies():
    """
    检查必要的依赖模块是否已安装
    """
    required_modules = {
        'PyQt5': 'PyQt5',
        'requests': 'requests',
        'websocket': 'websocket-client',
        'py_mini_racer': 'mini_racer',
        'betterproto': 'betterproto'
    }
    
    missing_modules = []
    
    for module_name, package_name in required_modules.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(package_name)
    
    if missing_modules:
        print("缺少以下依赖模块:")
        print(", ".join(missing_modules))
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    
    return True

def setup_application_style(app):
    """
    设置应用程序样式
    
    Args:
        app: QApplication实例
    """
    # 设置全局样式表
    app.setStyleSheet("""
        QApplication {
            font-family: "Microsoft YaHei", "SimHei", sans-serif;
            font-size: 12px;
        }
        
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QMessageBox {
            background-color: white;
            border: 1px solid #ddd;
        }
        
        QMessageBox QPushButton {
            min-width: 80px;
            min-height: 30px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QMessageBox QPushButton:hover {
            background-color: #45a049;
        }
        
        QMessageBox QPushButton:pressed {
            background-color: #3d8b40;
        }
    """)

def main():
    """
    主程序入口函数
    """
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("TikTok Virtual Streamer")
    app.setApplicationDisplayName("抖音虚拟主播数据监控")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TikTok Virtual Streamer Team")
    app.setOrganizationDomain("tiktok-virtual-streamer.com")
    
    # 设置应用程序图标（如果存在）
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 检查依赖
    if not check_dependencies():
        QMessageBox.critical(
            None, 
            "依赖检查失败", 
            "缺少必要的依赖模块，请查看控制台输出并安装相应模块。"
        )
        return 1
    
    # 设置应用程序样式
    setup_application_style(app)
    
    try:
        # 创建并显示主窗口
        main_window = MainWindow()
        main_window.show()
        
        # 显示欢迎信息
        main_window.status_bar.showMessage("欢迎使用TikTok Virtual Streamer！请输入直播间地址开始监控。")
        
    except Exception as e:
        QMessageBox.critical(
            None,
            "启动错误",
            f"应用程序启动失败:\n{str(e)}\n\n请检查配置和依赖是否正确。"
        )
        return 1
    
    # 启动事件循环
    return app.exec()

if __name__ == "__main__":
    # 设置异常处理
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行时发生未处理的异常: {e}")
        sys.exit(1)