# 🚀 Endless API - OpenAI API调用平台

一个功能完整的OpenAI API调用平台，支持多种AI交互模式和文件处理能力。

## ✨ 主要功能

- 💬 **智能聊天** - 支持GPT模型对话，保存聊天历史
- 📝 **文本补全** - 高效的文本生成和续写功能  
- 📊 **JSON批量处理** - 批量处理JSON格式提示词，支持并发处理
- 📎 **文件上传** - 支持图片识别(GPT-4o)和文档处理
- 👥 **用户管理** - 完整的用户注册、登录系统
- 📈 **使用统计** - 详细的API调用和token使用记录
- 🔐 **安全设计** - API密钥加密存储，会话管理
- 📱 **响应式界面** - 现代化的单页面应用设计
- ⌨️ **快捷操作** - 支持键盘快捷键和复制功能

## 🛠️ 技术栈

- **后端**: Flask + SQLAlchemy + SQLite
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **AI服务**: OpenAI API (GPT-3.5/GPT-4/GPT-4o)
- **数据库**: SQLite with ORM
- **安全**: SHA256密钥加密，会话认证

## 🚀 快速开始

### 方法1: 使用启动脚本（推荐）

```bash
# 克隆项目
git clone https://github.com/Ludandaye/endless-api.git
cd endless-api

# 运行启动脚本（自动处理环境和数据库）
python run_with_db.py
```

### 方法2: 手动配置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加您的配置

# 3. 初始化数据库
python init_db.py

# 4. 运行应用
python run.py
```

### 方法3: 生产环境部署

```bash
# 使用Gunicorn部署
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📋 使用说明

### 1. 用户注册/登录
- 首次使用需要注册账户
- 输入您的OpenAI API密钥进行登录
- API密钥将被安全加密存储

### 2. 聊天功能
- 选择GPT模型 (3.5-turbo, 4, 4o等)
- 支持上传图片进行视觉识别
- 拖拽文件到聊天区域快速上传
- 使用 Ctrl+Enter 发送消息

### 3. 文本补全
- 输入提示词获取AI生成内容
- 可调节温度、最大token等参数
- 支持多种生成模式

### 4. JSON批量处理
- 上传JSON格式的提示词数组
- 支持1-10并发处理
- 实时显示处理进度和统计信息
- 导出结果为JSON格式

### 5. 文件支持
- **图片**: JPG, PNG, GIF, WebP (最大10MB)
- **文档**: TXT, MD, DOC, PDF
- **功能**: 拖拽上传、预览、批量管理

## 🎯 功能特色

### JSON批量处理
```json
[
  {"prompt": "解释量子计算的基本原理"},
  {"prompt": "描述人工智能的发展历程"},
  {"prompt": "分析区块链技术的应用前景"}
]
```

### 文件上传与识别
- 支持多文件同时上传
- 图片自动识别分析  
- 文档内容提取处理
- 文件大小和数量统计

### 快捷键支持
- `Ctrl + Enter`: 发送消息
- `Ctrl + C`: 复制内容
- `Ctrl + U`: 上传文件
- `ESC`: 清除文件

## 📊 数据库结构

- **users**: 用户信息和API密钥管理
- **conversations**: 对话会话记录
- **messages**: 聊天消息详情
- **completions**: 文本补全记录  
- **usage_records**: API使用统计
- **system_configs**: 系统配置管理

## 🔒 安全特性

- API密钥SHA256加密存储
- 会话基础的身份验证
- 文件类型和大小验证
- SQL注入防护
- XSS攻击防护

## 📝 环境配置

创建 `.env` 文件:
```env
# Flask配置
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production

# 数据库配置  
DATABASE_URL=sqlite:///endless_api.db

# 日志配置
LOG_LEVEL=INFO

# OpenAI配置（可选）
OPENAI_API_KEY=your-openai-api-key
```

## 🌟 开发计划

- [ ] 支持更多AI模型 (Claude, Gemini等)
- [ ] 添加API调用限额管理
- [ ] 实现对话分享功能
- [ ] 添加插件系统
- [ ] 支持语音识别和TTS
- [ ] 移动端适配优化

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- OpenAI 提供强大的AI API服务
- Flask 社区提供优秀的Web框架
- 所有为开源社区做出贡献的开发者

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！ 