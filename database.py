from models import db, User, Conversation, Message, Completion, UsageRecord, SystemConfig
import hashlib
from datetime import datetime

def init_database(app):
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        print("数据库表创建完成！")

def create_user(api_key):
    """创建新用户"""
    # 生成API密钥哈希值
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # 生成脱敏显示的API密钥 - 更简洁的格式
    api_key_masked = api_key[:4] + '***' + api_key[-3:]
    
    user = User(
        api_key_hash=api_key_hash,
        api_key_masked=api_key_masked,
        last_login=datetime.utcnow()
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        print(f"创建用户失败: {e}")
        return None

def get_user_by_api_key(api_key):
    """根据API密钥获取用户"""
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return User.query.filter_by(api_key_hash=api_key_hash).first()

def update_user_login(user):
    """更新用户登录时间"""
    user.last_login = datetime.utcnow()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"更新用户登录时间失败: {e}")

def save_chat_message(user_id, conversation_id, role, content, model=None, tokens_used=None):
    """保存聊天消息"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        model=model,
        tokens_used=tokens_used
    )
    
    try:
        db.session.add(message)
        db.session.commit()
        return message
    except Exception as e:
        db.session.rollback()
        print(f"保存消息失败: {e}")
        return None

def get_or_create_conversation(user_id, title="新对话"):
    """获取或创建对话"""
    # 尝试获取用户最近的活跃对话
    conversation = Conversation.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(Conversation.updated_at.desc()).first()
    
    if not conversation:
        # 创建新对话
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        try:
            db.session.add(conversation)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"创建对话失败: {e}")
            return None
    
    return conversation

def save_completion(user_id, prompt, completion, model, max_tokens=None, temperature=None, tokens_used=None):
    """保存文本补全记录"""
    completion_record = Completion(
        user_id=user_id,
        prompt=prompt,
        completion=completion,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        tokens_used=tokens_used
    )
    
    try:
        db.session.add(completion_record)
        db.session.commit()
        return completion_record
    except Exception as e:
        db.session.rollback()
        print(f"保存补全记录失败: {e}")
        return None

def save_usage_record(user_id, api_type, model, tokens_used, cost=None, response_time=None, status='success'):
    """保存使用记录"""
    usage_record = UsageRecord(
        user_id=user_id,
        api_type=api_type,
        model=model,
        tokens_used=tokens_used,
        cost=cost,
        response_time=response_time,
        status=status
    )
    
    try:
        db.session.add(usage_record)
        db.session.commit()
        return usage_record
    except Exception as e:
        db.session.rollback()
        print(f"保存使用记录失败: {e}")
        return None

def get_user_conversations(user_id, limit=10):
    """获取用户的对话列表"""
    return Conversation.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(Conversation.updated_at.desc()).limit(limit).all()

def get_conversation_messages(conversation_id):
    """获取对话的所有消息"""
    return Message.query.filter_by(
        conversation_id=conversation_id
    ).order_by(Message.created_at.asc()).all()

def clear_user_conversations(user_id):
    """清除用户的所有对话"""
    try:
        # 将对话标记为非活跃状态而不是删除
        conversations = Conversation.query.filter_by(user_id=user_id, is_active=True).all()
        for conv in conversations:
            conv.is_active = False
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"清除对话失败: {e}")
        return False 