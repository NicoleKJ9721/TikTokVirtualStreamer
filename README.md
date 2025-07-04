# TikTok Virtual Streamer

抖音直播数据实时监控工具

## 项目简介

这是一个基于PyQt5开发的抖音直播数据监控工具，能够实时获取和显示抖音直播间的各种互动数据。通过WebSocket连接抖音直播间，实时解析并展示聊天消息、礼物信息、点赞、用户进场、关注等多种类型的直播互动数据，为直播数据分析和研究提供便利。

## 功能特性

### 🎯 核心功能

- **实时数据监控**: 通过WebSocket连接抖音直播间，实时获取直播互动数据
- **多类型消息解析**: 支持聊天、礼物、点赞、进场、关注等多种消息类型
- **现代化界面**: 基于PyQt5的图形化界面，支持暗色主题
- **数据统计**: 实时统计各类消息数量，提供数据分析
- **连接管理**: 支持连接/断开直播间，实时显示连接状态
- **多线程架构**: 后台数据获取，确保UI响应流畅

### 📊 支持的消息类型

- **聊天消息** (`ChatMessage`) - 观众发送的文字聊天内容
- **礼物消息** (`GiftMessage`) - 观众送礼物的详细信息，包括礼物名称和数量
- **点赞消息** (`LikeMessage`) - 观众点赞行为及点赞数量
- **进场消息** (`MemberMessage`) - 用户进入直播间，显示性别等信息
- **关注消息** (`SocialMessage`) - 观众关注主播的行为
- **统计信息** (`RoomUserSeqMessage`) - 直播间观看人数等统计数据
- **粉丝团消息** (`FansclubMessage`) - 粉丝团相关活动和互动
- **直播控制** (`ControlMessage`) - 直播开始/结束等状态变化
- **表情聊天** (`EmojiChatMessage`) - 聊天中的表情包消息
- **排行榜** (`RankMessage`) - 直播间各类排行榜信息

## 项目架构

```
TikTokVirtualStreamer/
├── gui_main.py              # 主程序入口
├── ui/                      # UI界面模块
│   ├── __init__.py
│   └── main_window.py       # 主窗口界面和交互逻辑
├── core/                    # 核心功能模块
│   ├── __init__.py
│   └── live_data_manager.py # 直播数据管理器，封装WebSocket连接
├── models/                  # 数据模型
│   ├── __init__.py
│   └── message_types.py     # 消息类型枚举定义
├── protobuf/               # Protocol Buffers定义
│   ├── __init__.py
│   ├── douyin.proto         # 抖音消息协议定义
│   ├── douyin.py           # 生成的Python Protocol Buffers类
│   └── readme.md           # Protocol Buffers说明
├── sign.js                 # JavaScript签名生成脚本
├── requirements.txt        # 项目依赖包列表
└── README.md              # 项目说明文档
```

### 架构设计原则

- **分层架构**: UI层、业务逻辑层、数据层清晰分离
- **模块化设计**: 功能模块独立，便于维护和扩展
- **信号槽机制**: 使用PyQt5信号槽实现跨线程安全通信
- **多线程架构**: 数据获取在后台线程进行，确保UI响应性
- **事件驱动**: 基于消息事件的实时数据处理机制

## 安装和使用

### 环境要求

- Python 3.8+
- macOS / Windows / Linux

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/NicoleKJ9721/TikTokVirtualStreamer.git
cd TikTokVirtualStreamer
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **运行程序**

```bash
python gui_main.py
```

### 使用方法

1. **启动应用程序**
   - 运行 `python gui_main.py`
   - 应用程序将显示主界面

2. **连接直播间**
   - 在"直播间地址"输入框中输入抖音直播间URL
   - 支持的URL格式:
     - `https://live.douyin.com/123456789`
     - `https://webcast.amemv.com/douyin/123456789`
     - 或直接输入直播间ID: `123456789`
   - 点击"🔗 连接直播间"按钮

3. **监控数据**
   - 连接成功后，实时消息将显示在右侧消息区域
   - 左侧面板显示直播间信息、连接状态和消息统计
   - 不同类型的消息会以不同颜色显示

4. **管理连接**
   - 点击"❌ 断开连接"停止监控
   - 点击"🗑️ 清空消息"清除消息显示

## 技术栈

### 前端界面

- **PyQt5**: 成熟稳定的Python GUI框架
- **自定义样式**: 支持暗色主题的现代化界面设计
- **响应式布局**: 自适应窗口大小的界面布局

### 后端核心

- **WebSocket**: 实时双向通信协议
- **Protocol Buffers**: 高效的二进制数据序列化
- **多线程**: 后台数据获取，确保UI流畅响应
- **信号槽**: PyQt5跨线程安全通信机制

### 数据处理

- **betterproto**: 现代化的Protocol Buffers Python实现
- **mini_racer**: 轻量级JavaScript执行引擎（用于签名生成）
- **requests**: 功能强大的HTTP请求库
- **websocket-client**: WebSocket客户端连接库

## 注意事项

⚠️ **重要提醒**

- 本项目仅用于学习研究交流，请勿用于商业用途
- 请遵守抖音平台的使用条款和相关法律法规
- 频繁请求可能导致IP被限制，请合理使用
- 数据获取依赖于抖音平台的接口，可能因平台更新而失效

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。