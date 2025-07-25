// ==================== 自定义助手功能 ====================

// 创建自定义助手
async function createCustomAssistant() {
    console.log('=== createCustomAssistant 函数被调用 ===');
    
    const requestInput = document.getElementById('assistant-request');
    const modelSelect = document.getElementById('assistant-model');
    const resultDiv = document.getElementById('assistant-result');
    const createBtn = document.getElementById('create-assistant-btn');
    
    console.log('DOM元素检查:');
    console.log('- requestInput:', requestInput);
    console.log('- modelSelect:', modelSelect);
    console.log('- resultDiv:', resultDiv);
    console.log('- createBtn:', createBtn);
    
    if (!requestInput || !modelSelect || !resultDiv || !createBtn) {
        console.error('找不到必要的DOM元素');
        alert('❌ 页面元素错误，请刷新页面重试');
        return;
    }
    
    const request = requestInput.value.trim();
    const model = modelSelect.value;
    
    console.log('输入值检查:');
    console.log('- request:', request);
    console.log('- model:', model);
    
    if (!request) {
        alert('❌ 请输入助手需求描述');
        return;
    }
    
    // 显示加载状态
    createBtn.disabled = true;
    createBtn.textContent = '🤖 创建中...';
    resultDiv.innerHTML = '<div class="loading">正在创建助手，请稍候...</div>';
    
    try {
        console.log('开始发送API请求...');
        const response = await axios.post('/api/create_assistant', {
            request: request,
            model: model
        });
        
        console.log('API响应:', response.data);
        
        if (response.data.success) {
            const conversation = response.data.conversation;
            
            // 显示成功结果
            resultDiv.innerHTML = `
                <div class="success-result">
                    <h4>✅ 助手创建成功！</h4>
                    <div class="assistant-info">
                        <p><strong>助手名称:</strong> ${conversation.title}</p>
                        <p><strong>创建时间:</strong> ${new Date(conversation.created_at).toLocaleString()}</p>
                        <p><strong>System Prompt:</strong></p>
                        <div class="system-prompt">${conversation.system_prompt}</div>
                    </div>
                    <div class="assistant-actions">
                        <button onclick="useAssistant(${conversation.id})" class="btn btn-primary">
                            💬 使用这个助手
                        </button>
                        <button onclick="copyAssistantResult()" class="btn btn-copy">
                            📋 复制结果
                        </button>
                    </div>
                </div>
            `;
            
            // 显示复制按钮
            document.getElementById('copy-assistant-btn').style.display = 'inline-block';
            
            // 清空输入框
            requestInput.value = '';
            
            // 更新助手列表
            loadAssistantList();
            
            console.log('助手创建成功:', conversation);
            
        } else {
            resultDiv.innerHTML = `<div class="error-result">❌ 创建失败: ${response.data.error}</div>`;
        }
        
    } catch (error) {
        console.error('创建助手失败:', error);
        console.error('错误详情:', {
            message: error.message,
            response: error.response?.data,
            status: error.response?.status,
            statusText: error.response?.statusText
        });
        
        const errorMsg = error.response?.data?.error || error.message || '未知错误';
        resultDiv.innerHTML = `<div class="error-result">❌ 创建失败: ${errorMsg}</div>`;
    } finally {
        // 恢复按钮状态
        createBtn.disabled = false;
        createBtn.textContent = '🤖 创建助手';
    }
}

// 清空助手表单
function clearAssistantForm() {
    const requestInput = document.getElementById('assistant-request');
    const resultDiv = document.getElementById('assistant-result');
    const copyBtn = document.getElementById('copy-assistant-btn');
    
    if (requestInput) {
        requestInput.value = '';
    }
    
    if (resultDiv) {
        resultDiv.innerHTML = '<div class="result-placeholder">助手创建结果将显示在这里...</div>';
    }
    
    if (copyBtn) {
        copyBtn.style.display = 'none';
    }
}

// 复制助手结果
async function copyAssistantResult() {
    const resultDiv = document.getElementById('assistant-result');
    const copyBtn = document.getElementById('copy-assistant-btn');
    
    if (!resultDiv) return;
    
    const content = resultDiv.textContent || resultDiv.innerText;
    
    if (!content || content.includes('助手创建结果将显示在这里')) {
        alert('❌ 没有可复制的内容');
        return;
    }
    
    await copyToClipboard(content, 'copy-assistant-btn', '助手创建结果');
}

// 使用助手
function useAssistant(conversationId) {
    // 切换到聊天选项卡
    switchTab('chat');
    
    // 设置当前对话ID（需要在聊天功能中实现）
    if (window.setCurrentConversation) {
        window.setCurrentConversation(conversationId);
    }
    
    // 显示提示
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.placeholder = '现在您可以与自定义助手对话了...';
        chatInput.focus();
    }
    
    console.log('切换到助手对话:', conversationId);
}

// 加载助手列表
async function loadAssistantList() {
    const assistantList = document.getElementById('assistant-list');
    
    if (!assistantList) return;
    
    try {
        const response = await axios.get('/api/conversations');
        
        if (response.data.conversations) {
            const assistants = response.data.conversations.filter(conv => conv.is_custom_assistant);
            
            if (assistants.length === 0) {
                assistantList.innerHTML = '<div class="assistant-placeholder">您还没有创建任何助手...</div>';
                return;
            }
            
            let html = '';
            assistants.forEach(assistant => {
                html += `
                    <div class="assistant-item">
                        <div class="assistant-header">
                            <h4>${assistant.title}</h4>
                            <span class="assistant-date">${new Date(assistant.created_at).toLocaleDateString()}</span>
                        </div>
                        <div class="assistant-preview">${assistant.system_prompt_preview || '无预览'}</div>
                        <div class="assistant-actions">
                            <button onclick="useAssistant(${assistant.id})" class="btn btn-sm btn-primary">
                                💬 使用
                            </button>
                        </div>
                    </div>
                `;
            });
            
            assistantList.innerHTML = html;
        }
        
    } catch (error) {
        console.error('加载助手列表失败:', error);
        assistantList.innerHTML = '<div class="error">加载助手列表失败</div>';
    }
}

// 页面加载时加载助手列表
document.addEventListener('DOMContentLoaded', function() {
    // 延迟加载助手列表，确保页面完全加载
    setTimeout(() => {
        loadAssistantList();
    }, 1000);
}); 