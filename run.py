#!/usr/bin/env python3
"""
OpenAI API调用平台启动脚本
自动安装依赖并启动应用
"""

import subprocess
import sys
import os

def install_requirements():
    """安装必需的依赖包"""
    requirements = [
        'flask',
        'flask-cors', 
        'openai',
        'python-dotenv',
        'gunicorn'
    ]
    
    print("正在安装依赖包...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"✗ {package} 安装失败")
            return False
    
    print("所有依赖包安装完成！")
    return True

def main():
    print("=" * 50)
    print("OpenAI API调用平台")
    print("=" * 50)
    
    # 检查是否已安装Flask
    try:
        import flask
        print("✓ Flask 已安装")
    except ImportError:
        print("Flask 未安装，正在安装依赖...")
        if not install_requirements():
            print("依赖安装失败，请手动安装")
            return
    
    print("\n程序功能:")
    print("🔑 用户登录：输入您的OpenAI API密钥")
    print("💬 智能对话：支持GPT模型聊天")
    print("📝 文本补全：文本生成和补全")
    print("⚙️ 参数调节：自定义模型参数")
    print("📊 使用统计：实时查看token消耗")
    
    print("\n启动应用...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动Flask应用
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == '__main__':
    main() 