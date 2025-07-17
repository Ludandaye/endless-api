from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    api_key_hash = db.Column(db.String(255), unique=True, nullable=False)  # API密钥哈希值
    api_key_masked = db.Column(db.String(50), nullable=False)  # 脱敏显示的API密钥
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联关系
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    completions = db.relationship('Completion', backref='user', lazy=True, cascade='all, delete-orphan')
    usage_records = db.relationship('UsageRecord', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.id}: {self.api_key_masked}>'

class Conversation(db.Model):
    """对话模型"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), default='新对话')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联关系
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Conversation {self.id}: {self.title}>'

class Message(db.Model):
    """消息模型"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # API调用相关信息
    model = db.Column(db.String(50))
    tokens_used = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Message {self.id}: {self.role}>'

class Completion(db.Model):
    """文本补全模型"""
    __tablename__ = 'completions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    completion = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # API调用参数
    max_tokens = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    tokens_used = db.Column(db.Integer)

    def __repr__(self):
        return f'<Completion {self.id}: {self.model}>'

class UsageRecord(db.Model):
    """使用记录模型"""
    __tablename__ = 'usage_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    api_type = db.Column(db.String(20), nullable=False)  # 'chat', 'completion'
    model = db.Column(db.String(50), nullable=False)
    tokens_used = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float)  # 估算成本
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # API响应信息
    response_time = db.Column(db.Float)  # 响应时间（秒）
    status = db.Column(db.String(20), default='success')  # 'success', 'error'

    def __repr__(self):
        return f'<UsageRecord {self.id}: {self.api_type} - {self.tokens_used} tokens>'

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SystemConfig {self.key}: {self.value}>' 