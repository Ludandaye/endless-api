#!/usr/bin/env python3
"""
数据库初始化脚本
运行此脚本来创建数据库表
"""

import os
import sys
from flask import Flask
from config import config
from models import db, SystemConfig

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    config_name = os.environ.get('FLASK_ENV') or 'development'
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    db.init_app(app)
    
    return app

def main():
    """主函数"""
    print("开始初始化数据库...")
    
    # 创建Flask应用
    app = create_app()
    
    # 初始化数据库
    with app.app_context():
        try:
            # 删除现有表（如果存在）
            print("删除现有数据库表...")
            db.drop_all()
            print("已删除现有数据库表")
            
            # 创建所有表
            print("创建数据库表...")
            db.create_all()
            print("数据库表创建成功！")
            
            # 插入一些初始配置
            print("插入初始配置...")
            
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
                    print(f"添加配置: {config.key} = {config.value}")
            
            db.session.commit()
            print("初始配置数据插入成功！")
            
            # 显示数据库信息
            print("\n数据库信息:")
            print(f"数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"数据库文件: {app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')}")
            
            # 显示表信息
            print("\n已创建的数据库表:")
            from models import User, Conversation, Message, Completion, UsageRecord
            tables = [User, Conversation, Message, Completion, UsageRecord, SystemConfig]
            for table in tables:
                print(f"- {table.__tablename__}")
            
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            db.session.rollback()
            return False
        
    print("\n数据库初始化完成！")
    print("现在您可以运行应用了: python app.py")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 