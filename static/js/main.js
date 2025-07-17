// 主页面JavaScript
let isLoading = false;
let currentTab = 'chat';

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面
    initializePage();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 检查系统状态
    checkStatus();
});

// 初始化页面
function initializePage() {
    // 设置默认选项卡
    switchTab('chat');
    
    // 初始化聊天界面
    initializeChatInterface();
}

// 绑定事件监听器
function bindEventListeners() {
    // 聊天输入框回车键监听
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    // 补全文本区域快捷键监听
    const completionPrompt = document.getElementById('completion-prompt');
    if (completionPrompt) {
        completionPrompt.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                generateCompletion();
            }
        });
    }
    
    // 表单变化监听
    bindFormChangeListeners();
}

// 绑定表单变化监听器
function bindFormChangeListeners() {
    // 聊天模型变化
    const chatModel = document.getElementById('chat-model');
    if (chatModel) {
        chatModel.addEventListener('change', function() {
            console.log('聊天模型切换到:', this.value);
        });
    }
    
    // 补全模型变化
    const completionModel = document.getElementById('completion-model');
    if (completionModel) {
        completionModel.addEventListener('change', function() {
            console.log('补全模型切换到:', this.value);
        });
    }
}

// 初始化聊天界面
function initializeChatInterface() {
    const messagesDiv = document.getElementById('chat-messages');
    if (messagesDiv) {
        // 清空并显示欢迎信息
        messagesDiv.innerHTML = '<div class="chat-placeholder">开始对话...</div>';
    }
}

// 检查系统状态
async function checkStatus() {
    try {
        const response = await axios.get('/api/status');
        const status = response.data;
        
        updateStatusIndicator(status);
        updateUserInfo(status);
        
        if (!status.logged_in) {
            // 如果未登录，重定向到登录页面
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('状态检查失败:', error);
        updateStatusIndicator({ 
            status: 'error', 
            logged_in: false 
        });
    }
}

// 更新状态指示器
function updateStatusIndicator(status) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (!indicator || !statusText) return;
    
    // 移除所有状态类
    indicator.classList.remove('online', 'offline', 'loading');
    
    if (status.logged_in && status.status === 'running') {
        indicator.classList.add('online');
        statusText.textContent = '系统正常运行，已登录';
    } else if (!status.logged_in) {
        indicator.classList.add('offline');
        statusText.textContent = '未登录';
    } else {
        indicator.classList.add('offline');
        statusText.textContent = '无法连接到服务器';
    }
}

// 更新用户信息
function updateUserInfo(status) {
    const apiKeyMasked = document.getElementById('apiKeyMasked');
    
    if (!apiKeyMasked) return;
    
    if (status.logged_in && status.api_key_masked) {
        apiKeyMasked.textContent = status.api_key_masked;
    } else {
        apiKeyMasked.textContent = '未登录';
    }
}

// 退出登录
async function logout() {
    try {
        await axios.post('/logout');
        window.location.href = '/login';
    } catch (error) {
        console.error('退出登录失败:', error);
        alert('退出登录失败: ' + (error.response?.data?.error || error.message));
    }
}

// 切换选项卡
function switchTab(tabName) {
    // 隐藏所有内容面板
    document.querySelectorAll('.tab-content').forEach(panel => {
        panel.classList.remove('active');
        panel.classList.add('hidden');
    });
    
    // 重置所有选项卡按钮样式
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // 显示选中的面板
    const targetPanel = document.getElementById(tabName + '-panel');
    if (targetPanel) {
        targetPanel.classList.remove('hidden');
        targetPanel.classList.add('active');
    }
    
    // 激活选中的选项卡按钮
    const activeTab = document.getElementById(tabName + '-tab');
    if (activeTab) {
        activeTab.classList.add('active');
    }
    
    // 更新当前选项卡
    currentTab = tabName;
    
    // 选项卡切换后的处理
    onTabSwitch(tabName);
}

// 选项卡切换后的处理
function onTabSwitch(tabName) {
    if (tabName === 'chat') {
        // 聚焦到聊天输入框
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.focus();
        }
    } else if (tabName === 'completion') {
        // 聚焦到补全提示框
        const completionPrompt = document.getElementById('completion-prompt');
        if (completionPrompt) {
            completionPrompt.focus();
        }
    }
}

// 发送聊天消息
async function sendChatMessage() {
    if (isLoading) return;
    
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 清空输入框
    input.value = '';
    
    // 禁用输入
    setLoading(true);
    
    // 添加用户消息到聊天窗口
    addMessageToChat('user', message);
    
    try {
        // 获取聊天设置
        const chatSettings = getChatSettings();
        
        // 发送请求
        const response = await axios.post('/api/chat', {
            message: message,
            ...chatSettings
        });
        
        // 添加助手回复到聊天窗口
        addMessageToChat('assistant', response.data.response);
        
        // 显示使用统计（如果需要）
        if (response.data.usage) {
            console.log('Token使用情况:', response.data.usage);
        }
        
    } catch (error) {
        handleApiError(error, 'sendChatMessage');
        addMessageToChat('error', '错误: ' + getErrorMessage(error));
    } finally {
        setLoading(false);
        // 重新聚焦到输入框
        input.focus();
    }
}

// 获取聊天设置
function getChatSettings() {
    return {
        model: getElementValue('chat-model') || 'gpt-3.5-turbo',
        max_tokens: parseInt(getElementValue('chat-max-tokens')) || 1000,
        temperature: parseFloat(getElementValue('chat-temperature')) || 0.7
    };
}

// 获取补全设置
function getCompletionSettings() {
    return {
        model: getElementValue('completion-model') || 'gpt-3.5-turbo-instruct',
        max_tokens: parseInt(getElementValue('completion-max-tokens')) || 1000,
        temperature: parseFloat(getElementValue('completion-temperature')) || 0.7
    };
}

// 安全获取元素值
function getElementValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : null;
}

// 添加消息到聊天窗口
function addMessageToChat(role, content) {
    const messagesDiv = document.getElementById('chat-messages');
    if (!messagesDiv) return;
    
    // 如果是第一条消息，清除占位符
    const placeholder = messagesDiv.querySelector('.chat-placeholder');
    if (placeholder) {
        messagesDiv.innerHTML = '';
    }
    
    // 创建消息元素
    const messageDiv = createMessageElement(role, content);
    messagesDiv.appendChild(messageDiv);
    
    // 滚动到底部
    scrollToBottom(messagesDiv);
}

// 创建消息元素
function createMessageElement(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const roleSpan = document.createElement('div');
    roleSpan.className = `message-role ${role}`;
    roleSpan.textContent = getRoleDisplayName(role);
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(roleSpan);
    messageDiv.appendChild(contentDiv);
    
    return messageDiv;
}

// 获取角色显示名称
function getRoleDisplayName(role) {
    const roleNames = {
        'user': '用户',
        'assistant': 'AI助手',
        'error': '错误'
    };
    return roleNames[role] || role;
}

// 滚动到底部
function scrollToBottom(element) {
    if (element) {
        element.scrollTop = element.scrollHeight;
    }
}

// 清除聊天历史
async function clearHistory() {
    try {
        await axios.post('/api/clear_history');
        
        // 清空聊天窗口
        const messagesDiv = document.getElementById('chat-messages');
        if (messagesDiv) {
            messagesDiv.innerHTML = '<div class="chat-placeholder">聊天历史已清除，开始新的对话...</div>';
        }
        
    } catch (error) {
        handleApiError(error, 'clearHistory');
        alert('清除历史失败: ' + getErrorMessage(error));
    }
}

// 生成文本补全
async function generateCompletion() {
    if (isLoading) return;
    
    const promptElement = document.getElementById('completion-prompt');
    const prompt = promptElement.value.trim();
    
    if (!prompt) {
        alert('请输入提示文本');
        return;
    }
    
    setLoading(true);
    
    const resultDiv = document.getElementById('completion-result');
    if (resultDiv) {
        resultDiv.innerHTML = '<div class="result-loading">生成中...</div>';
    }
    
    try {
        // 获取补全设置
        const completionSettings = getCompletionSettings();
        
        // 发送请求
        const response = await axios.post('/api/completion', {
            prompt: prompt,
            ...completionSettings
        });
        
        // 显示结果
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="result-content">${response.data.completion}</div>`;
        }
        
        // 显示使用统计
        if (response.data.usage) {
            console.log('Token使用情况:', response.data.usage);
        }
        
    } catch (error) {
        handleApiError(error, 'generateCompletion');
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="result-error">错误: ${getErrorMessage(error)}</div>`;
        }
    } finally {
        setLoading(false);
    }
}

// 处理API错误
function handleApiError(error, context) {
    console.error(`${context} error:`, error);
    
    if (error.response?.status === 401) {
        // 未授权，重定向到登录页面
        window.location.href = '/login';
        return;
    }
    
    // 其他错误记录但不重定向
}

// 获取错误消息
function getErrorMessage(error) {
    if (error.response?.data?.error) {
        return error.response.data.error;
    } else if (error.request) {
        return '网络连接失败';
    } else {
        return error.message || '未知错误';
    }
}

// 设置加载状态
function setLoading(loading) {
    isLoading = loading;
    
    // 更新按钮状态
    updateButtonStates(loading);
    
    // 更新输入框状态
    updateInputStates(loading);
}

// 更新按钮状态
function updateButtonStates(disabled) {
    const buttons = [
        'send-chat-btn',
        'generate-completion-btn',
        'clear-history-btn'
    ];
    
    buttons.forEach(id => {
        const button = document.getElementById(id);
        if (button) {
            button.disabled = disabled;
            if (disabled) {
                button.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                button.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        }
    });
}

// 更新输入框状态
function updateInputStates(disabled) {
    const inputs = [
        'chat-input',
        'completion-prompt'
    ];
    
    inputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.disabled = disabled;
        }
    });
}

// 格式化token数量
function formatTokenCount(count) {
    if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'K';
    }
    return count.toString();
}

// 复制文本到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        // 回退方法
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        } catch (err) {
            document.body.removeChild(textArea);
            return false;
        }
    }
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 防抖函数
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// 导出主要函数供HTML调用
window.logout = logout;
window.switchTab = switchTab;
window.sendChatMessage = sendChatMessage;
window.clearHistory = clearHistory;
window.generateCompletion = generateCompletion; 