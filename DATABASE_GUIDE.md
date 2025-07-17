# endless-api 数据库使用指南

## 🏗️ 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
# 方法一：使用初始化脚本（推荐）
python init_db.py

# 方法二：直接启动应用（自动初始化）
python run_with_db.py
```

### 3. 启动应用
```bash
# 简单启动
python app.py

# 或使用增强启动脚本
python run_with_db.py
```

## 📊 数据库结构

### 用户表 (users)
- `id`: 用户ID（主键）
- `api_key_hash`: API密钥哈希值（安全存储）
- `api_key_masked`: 脱敏显示的API密钥
- `created_at`: 创建时间
- `last_login`: 最后登录时间
- `is_active`: 是否活跃

### 对话表 (conversations)
- `id`: 对话ID（主键）
- `user_id`: 用户ID（外键）
- `title`: 对话标题
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `is_active`: 是否活跃

### 消息表 (messages)
- `id`: 消息ID（主键）
- `conversation_id`: 对话ID（外键）
- `role`: 角色（user/assistant/system）
- `content`: 消息内容
- `model`: 使用的模型
- `tokens_used`: 使用的Token数

### 补全记录表 (completions)
- `id`: 记录ID（主键）
- `user_id`: 用户ID（外键）
- `prompt`: 提示文本
- `completion`: 补全结果
- `model`: 使用的模型
- `tokens_used`: 使用的Token数

### 使用记录表 (usage_records)
- `id`: 记录ID（主键）
- `user_id`: 用户ID（外键）
- `api_type`: API类型（chat/completion）
- `model`: 使用的模型
- `tokens_used`: 使用的Token数
- `cost`: 估算成本
- `response_time`: 响应时间

### 系统配置表 (system_configs)
- `id`: 配置ID（主键）
- `key`: 配置键
- `value`: 配置值
- `description`: 配置描述

## 🔧 数据库操作

### 查看数据库
```bash
# 如果安装了sqlite3
sqlite3 endless_api_dev.db

# SQLite命令
.tables              # 查看所有表
.schema users        # 查看用户表结构
SELECT * FROM users; # 查询用户数据
.exit               # 退出
```

### 重置数据库
```bash
# 删除数据库文件
rm endless_api_dev.db

# 重新初始化
python init_db.py
```

### 备份数据库
```bash
# 复制数据库文件
cp endless_api_dev.db backup_$(date +%Y%m%d_%H%M%S).db
```

## 🌍 环境配置

### 开发环境
```bash
export FLASK_ENV=development
```

### 生产环境
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=sqlite:///endless_api_prod.db
```

## 📈 功能特点

✅ **用户管理**: 安全的API密钥存储和用户认证  
✅ **对话历史**: 完整的聊天记录保存和恢复  
✅ **使用统计**: Token使用量和成本跟踪  
✅ **数据安全**: 密钥哈希存储，不保存明文  
✅ **系统配置**: 灵活的配置管理系统  
✅ **扩展性**: 易于添加新功能和字段  

## 🛠️ 维护命令

```bash
# 查看数据库状态
python -c "from app import app, db; from models import User; app.app_context().push(); print(f'用户数: {User.query.count()}')"

# 清理无效对话
python -c "from app import app, db; from models import Conversation; app.app_context().push(); Conversation.query.filter_by(is_active=False).delete(); db.session.commit(); print('清理完成')"
```

## 🆘 故障排除

### 常见问题

1. **导入错误**: 确保所有依赖已安装
2. **数据库锁定**: 关闭其他访问数据库的程序
3. **权限问题**: 确保有写入权限
4. **配置错误**: 检查环境变量设置

### 日志查看
应用日志会显示详细的操作信息，包括：
- 用户登录/注册
- API调用记录
- 错误信息
- 数据库操作状态

## 📝 下一步

数据库已经完成设置！您现在可以：

1. 🚀 启动应用: `python run_with_db.py`
2. 🌐 访问: http://localhost:5000
3. 🔑 使用您的OpenAI API密钥登录
4. 💬 开始聊天和使用补全功能

所有的操作都会自动保存到数据库中！ 