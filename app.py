from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from openai import OpenAI
import os
from datetime import datetime
import logging
import time

# 导入数据库相关模块
from config import config
from models import db, Conversation
from database import (
    create_user, get_user_by_api_key, update_user_login,
    save_chat_message, get_or_create_conversation, save_completion,
    save_usage_record, get_user_conversations, get_conversation_messages,
    clear_user_conversations, create_custom_assistant
)

def create_app():
    """创建和配置Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    config_name = os.environ.get('FLASK_ENV') or 'development'
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    
    # 配置日志
    logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))
    logger = logging.getLogger(__name__)
    
    return app

app = create_app()
logger = logging.getLogger(__name__)

def get_openai_client():
    """获取当前用户的OpenAI客户端"""
    api_key = session.get('api_key')
    if not api_key:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"创建OpenAI客户端失败: {str(e)}")
        return None

def get_current_user():
    """获取当前用户"""
    api_key = session.get('api_key')
    if not api_key:
        return None
    return get_user_by_api_key(api_key)

def verify_api_key(api_key):
    """验证API密钥是否有效"""
    try:
        # 简化客户端初始化，避免参数冲突
        client = OpenAI(api_key=api_key)
        
        # 尝试获取模型列表来验证密钥
        try:
            models = client.models.list()
            # 检查是否成功获取到模型列表
            if models and hasattr(models, 'data') and len(models.data) > 0:
                logger.info(f"API密钥验证成功，可用模型数量: {len(models.data)}")
                return True
            else:
                logger.warning("API密钥验证失败：未获取到模型列表")
                return False
        except Exception as api_error:
            logger.error(f"API调用失败: {str(api_error)}")
            return False
            
    except Exception as e:
        logger.error(f"OpenAI客户端初始化失败: {str(e)}")
        return False

@app.route('/')
def home():
    """主页面 - 检查是否已登录"""
    if 'api_key' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({'error': '请输入API密钥'}), 400
    
    if not api_key.startswith('sk-'):
        return jsonify({'error': 'API密钥格式不正确'}), 400
    
    # 验证API密钥
    if not verify_api_key(api_key):
        return jsonify({'error': 'API密钥无效或已过期'}), 401
    
    try:
        # 查找或创建用户
        user = get_user_by_api_key(api_key)
        if not user:
            user = create_user(api_key)
            if not user:
                return jsonify({'error': '用户创建失败'}), 500
            logger.info(f"新用户注册: {user.api_key_masked}")
        else:
            # 更新登录时间
            update_user_login(user)
            logger.info(f"用户登录: {user.api_key_masked}")
        
        # 保存到会话
        session['api_key'] = api_key
        session['user_id'] = user.id
        session['user_masked'] = user.api_key_masked
        session.permanent = True
        
        return jsonify({'success': True, 'message': '登录成功'})
        
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({'error': '登录失败，请重试'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """退出登录"""
    user_id = session.get('user_id')
    if user_id:
        logger.info(f"用户退出登录: {session.get('user_masked')}")
    
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})

@app.route('/api/status')
def api_status():
    """获取API状态"""
    if 'api_key' not in session:
        return jsonify({
            'logged_in': False,
            'status': 'not_logged_in'
        })
    
    user = get_current_user()
    if not user:
        return jsonify({
            'logged_in': False,
            'status': 'user_not_found'
        })
    
    return jsonify({
        'logged_in': True,
        'status': 'running',
        'user_id': user.id,
        'last_login': user.last_login.isoformat() if user.last_login else None
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """聊天API - 支持文本和图片"""
    if 'api_key' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    
    data = request.get_json()
    message = data.get('message', '').strip()
    model = data.get('model', 'gpt-3.5-turbo')
    max_tokens = data.get('max_tokens', 1000)
    temperature = data.get('temperature', 0.7)
    images = data.get('images', [])
    conversation_id = data.get('conversation_id')  # 新增：指定对话ID
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        # 获取或创建对话
        if conversation_id:
            # 使用指定的对话
            conversation = Conversation.query.filter_by(
                id=conversation_id, 
                user_id=user.id
            ).first()
            if not conversation:
                return jsonify({'error': '对话不存在'}), 404
        else:
            # 获取或创建新对话
            conversation = get_or_create_conversation(user.id)
            if not conversation:
                return jsonify({'error': '创建对话失败'}), 500
        
        # 保存用户消息
        save_chat_message(user.id, conversation.id, 'user', message)
        
        # 调用OpenAI API
        start_time = time.time()
        client = get_openai_client()
        
        # 获取对话历史
        messages = get_conversation_messages(conversation.id)
        chat_messages = []
        
        # 如果有自定义system prompt，添加到消息开头
        if conversation.system_prompt:
            chat_messages.append({
                'role': 'system',
                'content': conversation.system_prompt
            })
        
        # 添加其他消息
        for msg in messages:
            if msg.role != 'system':  # 跳过已添加的system消息
                chat_messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
        
        # 如果有图片且模型支持视觉，构建特殊的消息格式
        if images and model in ['gpt-4o', 'gpt-4-vision-preview', 'gpt-4o-mini']:
            # 为支持视觉的模型构建消息
            content_parts = [{"type": "text", "text": message}]
            
            for image in images:
                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image['data']
                    }
                })
            
            # 替换最后一条用户消息为多模态消息
            if chat_messages and chat_messages[-1]['role'] == 'user':
                chat_messages[-1]['content'] = content_parts
        
        response = client.chat.completions.create(
            model=model,
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response_time = time.time() - start_time
        assistant_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # 保存AI回复
        save_chat_message(user.id, conversation.id, 'assistant', assistant_message, model, tokens_used)
        
        # 保存使用记录
        save_usage_record(
            user_id=user.id,
            api_type='chat',
            model=model,
            tokens_used=tokens_used,
            response_time=response_time,
            status='success'
        )
        
        logger.info(f"聊天成功 - 用户: {user.api_key_masked}, 模型: {model}, Tokens: {tokens_used}, 图片数: {len(images)}")
        
        return jsonify({
            'response': assistant_message,
            'model': model,
            'conversation_id': conversation.id,
            'conversation_title': conversation.title,
            'usage': {
                'total_tokens': tokens_used,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
        })
        
    except Exception as e:
        logger.error(f"聊天API错误: {e}")
        
        # 保存错误记录
        save_usage_record(
            user_id=user.id,
            api_type='chat',
            model=model,
            tokens_used=0,
            status='error'
        )
        
        return jsonify({'error': f'聊天失败: {str(e)}'}), 500

@app.route('/api/completion', methods=['POST'])
def api_completion():
    """文本补全API"""
    if 'api_key' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    model = data.get('model', 'gpt-3.5-turbo-instruct')
    max_tokens = data.get('max_tokens', 1000)
    temperature = data.get('temperature', 0.7)
    
    if not prompt:
        return jsonify({'error': '提示文本不能为空'}), 400
    
    try:
        start_time = time.time()
        client = get_openai_client()
        
        response = client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response_time = time.time() - start_time
        completion_text = response.choices[0].text
        tokens_used = response.usage.total_tokens
        
        # 保存补全记录
        save_completion(
            user_id=user.id,
            prompt=prompt,
            completion=completion_text,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tokens_used=tokens_used
        )
        
        # 保存使用记录
        save_usage_record(
            user_id=user.id,
            api_type='completion',
            model=model,
            tokens_used=tokens_used,
            response_time=response_time,
            status='success'
        )
        
        logger.info(f"补全成功 - 用户: {user.api_key_masked}, 模型: {model}, Tokens: {tokens_used}")
        
        return jsonify({
            'completion': completion_text,
            'model': model,
            'usage': {
                'total_tokens': tokens_used,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
        })
        
    except Exception as e:
        logger.error(f"补全API错误: {e}")
        
        # 保存错误记录
        save_usage_record(
            user_id=user.id,
            api_type='completion',
            model=model,
            tokens_used=0,
            status='error'
        )
        
        return jsonify({'error': f'文本补全失败: {str(e)}'}), 500

@app.route('/api/clear_history', methods=['POST'])
def api_clear_history():
    """清除聊天历史"""
    if 'api_key' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    
    try:
        success = clear_user_conversations(user.id)
        if success:
            logger.info(f"清除聊天历史 - 用户: {user.api_key_masked}")
            return jsonify({'success': True, 'message': '聊天历史已清除'})
        else:
            return jsonify({'error': '清除历史失败'}), 500
            
    except Exception as e:
        logger.error(f"清除历史错误: {e}")
        return jsonify({'error': f'清除历史失败: {str(e)}'}), 500

@app.route('/api/conversations')
def api_conversations():
    """获取用户对话列表"""
    if 'api_key' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    
    try:
        conversations = get_user_conversations(user.id)
        conv_list = []
        for conv in conversations:
            conv_data = {
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': len(conv.messages),
                'is_custom_assistant': bool(conv.system_prompt)  # 是否为自定义助手
            }
            
            # 如果是自定义助手，添加system_prompt预览
            if conv.system_prompt:
                conv_data['system_prompt_preview'] = conv.system_prompt[:100] + '...' if len(conv.system_prompt) > 100 else conv.system_prompt
            
            conv_list.append(conv_data)
        
        return jsonify({'conversations': conv_list})
        
    except Exception as e:
        logger.error(f"获取对话列表错误: {e}")
        return jsonify({'error': f'获取对话失败: {str(e)}'}), 500

@app.route('/api/create_assistant', methods=['POST'])
def api_create_assistant():
    """创建自定义对话助手"""
    if 'api_key' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    
    data = request.get_json()
    user_request = data.get('request', '').strip()
    model = data.get('model', 'gpt-4')
    
    if not user_request:
        return jsonify({'error': '请描述您需要的助手功能'}), 400
    
    try:
        # 创建自定义助手
        api_key = session.get('api_key')
        conversation = create_custom_assistant(user.id, user_request, api_key, model)
        
        if not conversation:
            return jsonify({'error': '创建助手失败，请重试'}), 500
        
        logger.info(f"创建自定义助手 - 用户: {user.api_key_masked}, 需求: {user_request[:50]}...")
        
        return jsonify({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'system_prompt': conversation.system_prompt,
                'created_at': conversation.created_at.isoformat()
            },
            'message': f'已创建"{conversation.title}"助手'
        })
        
    except Exception as e:
        logger.error(f"创建助手错误: {e}")
        return jsonify({'error': f'创建助手失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 