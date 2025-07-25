# 📁 endless-api 项目结构

## 🎯 项目概述
endless-api 是一个功能完整的OpenAI API调用平台，支持多种AI交互模式和文件处理能力。

## 📂 目录结构

```
endless-api/
├── 📁 templates/                 # HTML模板文件
│   ├── index.html               # 主页面模板
│   └── login.html               # 登录页面模板
├── 📁 static/                   # 静态资源文件
│   ├── 📁 js/                   # JavaScript文件
│   │   ├── assistant.js         # 自定义助手功能
│   │   ├── login.js             # 登录页面脚本
│   │   └── main.js              # 主页面脚本
│   └── 📁 css/                  # CSS样式文件
├── 📁 instance/                 # 实例文件夹（数据库等）
├── 📁 .venv/                    # Python虚拟环境
├── 📁 .git/                     # Git版本控制
├── 📁 .idea/                    # IDE配置文件
├── app.py                       # 主应用文件
├── database.py                  # 数据库操作
├── models.py                    # 数据模型
├── config.py                    # 配置文件
├── run.py                       # 应用启动脚本
├── run_with_db.py              # 带数据库初始化的启动脚本
├── init_db.py                   # 数据库初始化脚本
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git忽略文件
├── README.md                    # 项目说明文档
├── DATABASE_GUIDE.md           # 数据库使用指南
└── PROJECT_STRUCTURE.md        # 项目结构文档（本文件）
```

## 🚀 核心功能

### 1. 用户管理
- ✅ 用户注册和登录
- ✅ API密钥验证
- ✅ 会话管理
- ✅ 安全退出

### 2. 聊天对话
- ✅ 支持多种GPT模型
- ✅ 聊天历史保存
- ✅ 文件上传和图片识别
- ✅ 自定义助手功能

### 3. 文本补全
- ✅ 支持多种补全模型
- ✅ 参数可调节
- ✅ 结果保存

### 4. JSON批量处理
- ✅ 批量API调用
- ✅ 并发处理
- ✅ 进度显示
- ✅ 结果统计

### 5. 自定义助手
- ✅ 自然语言描述助手需求
- ✅ AI生成system prompt
- ✅ 助手列表管理
- ✅ 一键使用助手

### 6. 文件处理
- ✅ 图片识别（GPT-4o）
- ✅ 文档处理
- ✅ 拖拽上传
- ✅ 文件预览

## 🔧 技术栈

- **后端**: Flask + SQLAlchemy + SQLite
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **AI服务**: OpenAI API (GPT-3.5/GPT-4/GPT-4o)
- **数据库**: SQLite with ORM
- **安全**: SHA256密钥加密，会话认证

## 📊 数据库结构

### 核心表
1. **users** - 用户信息
2. **conversations** - 对话记录
3. **messages** - 消息内容
4. **completions** - 补全记录
5. **usage_records** - 使用统计
6. **system_configs** - 系统配置

## 🎨 界面特性

- ✅ 响应式设计
- ✅ 现代化UI
- ✅ 键盘快捷键
- ✅ 复制功能
- ✅ 进度指示
- ✅ 错误处理

## 🔐 安全特性

- ✅ API密钥加密存储
- ✅ 会话管理
- ✅ 输入验证
- ✅ 错误日志
- ✅ 敏感信息隐藏

## 📝 使用说明

1. **安装依赖**: `pip install -r requirements.txt`
2. **初始化数据库**: `python init_db.py`
3. **启动应用**: `python run_with_db.py`
4. **访问应用**: http://localhost:8080

## 🎯 项目亮点

- 🚀 **功能完整**: 涵盖OpenAI API的主要功能
- 🎨 **界面美观**: 现代化响应式设计
- 🔐 **安全可靠**: 完善的用户认证和数据保护
- 📊 **数据管理**: 完整的数据库结构和统计功能
- 🤖 **智能助手**: 创新的自定义助手功能
- 📁 **文件处理**: 支持多种文件格式和图片识别

---

*最后更新: 2025年7月25日* 