#!/usr/bin/env python3
"""
包含数据库初始化的应用启动脚本
"""

import os
import sys
from app import app, db

def check_database():
    """检查数据库是否存在，如果不存在则初始化"""
    db_file = 'endless_api_dev.db'
    
    if not os.path.exists(db_file):
        print("数据库文件不存在，正在初始化...")
        with app.app_context():
            try:
                # 导入所有模型
                from models import User, Conversation, Message, Completion, UsageRecord, SystemConfig
                
                # 创建所有表
                db.create_all()
                
                # 插入初始配置
                configs = [
                    SystemConfig(key='app_name', value='endless-api', description='应用名称'),
                    SystemConfig(key='version', value='1.0.0', description='应用版本'),
                    SystemConfig(key='max_conversations', value='50', description='每用户最大对话数'),
                    SystemConfig(key='max_messages_per_conversation', value='100', description='每对话最大消息数'),
                ]
                
                for config in configs:
                    existing = SystemConfig.query.filter_by(key=config.key).first()
                    if not existing:
                        db.session.add(config)
                
                db.session.commit()
                print("数据库初始化完成！")
                
            except Exception as e:
                print(f"数据库初始化失败: {e}")
                db.session.rollback()
                return False
    else:
        print("数据库文件已存在，跳过初始化")
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 endless-api 启动中...")
    print("=" * 50)
    
    # 检查并初始化数据库
    if not check_database():
        print("❌ 数据库初始化失败，退出启动")
        sys.exit(1)
    
    print("\n📊 数据库状态: ✅ 就绪")
    print("🌐 应用地址: http://localhost:8080")
    print("📝 日志级别: INFO")
    print("\n" + "=" * 50)
    print("应用正在启动，请稍候...")
    print("=" * 50)
    
    # 启动Flask应用
    try:
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 