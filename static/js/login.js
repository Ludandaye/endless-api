// 登录页面JavaScript
let isLoading = false;

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 聚焦到API密钥输入框
    document.getElementById('apiKey').focus();
    
    // 绑定事件监听器
    bindEventListeners();
});

// 绑定事件监听器
function bindEventListeners() {
    // 登录表单提交
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }
    
    // 输入框回车键提交
    const apiKeyInput = document.getElementById('apiKey');
    if (apiKeyInput) {
        apiKeyInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleLoginSubmit(e);
            }
        });
    }
}

// 处理登录表单提交
async function handleLoginSubmit(e) {
    e.preventDefault();
    
    // 防止重复提交
    if (isLoading) return;
    
    const apiKey = document.getElementById('apiKey').value.trim();
    
    // 隐藏错误信息
    hideError();
    
    // 基本验证
    if (!validateApiKey(apiKey)) {
        return;
    }
    
    // 显示加载状态
    setLoadingState(true);
    
    try {
        const success = await submitLogin(apiKey);
        if (success) {
            // 登录成功，跳转到主页
            window.location.href = '/';
        }
    } catch (error) {
        handleLoginError(error);
    } finally {
        setLoadingState(false);
    }
}

// 验证API密钥格式
function validateApiKey(apiKey) {
    if (!apiKey) {
        showError('请输入API密钥');
        return false;
    }
    
    if (!apiKey.startsWith('sk-')) {
        showError('API密钥格式不正确，应该以 sk- 开头');
        return false;
    }
    
    if (apiKey.length < 20) {
        showError('API密钥长度不正确');
        return false;
    }
    
    return true;
}

// 提交登录请求
async function submitLogin(apiKey) {
    try {
        const response = await axios.post('/login', {
            api_key: apiKey
        });
        
        return response.data.success;
    } catch (error) {
        throw error;
    }
}

// 处理登录错误
function handleLoginError(error) {
    let errorMsg = '登录失败，请重试';
    
    if (error.response) {
        // 服务器返回错误
        if (error.response.data && error.response.data.error) {
            errorMsg = error.response.data.error;
        } else if (error.response.status === 401) {
            errorMsg = 'API密钥无效，请检查您的密钥';
        } else if (error.response.status >= 500) {
            errorMsg = '服务器错误，请稍后重试';
        }
    } else if (error.request) {
        // 网络错误
        errorMsg = '网络连接失败，请检查网络连接';
    }
    
    showError(errorMsg);
}

// 设置加载状态
function setLoadingState(loading) {
    isLoading = loading;
    
    const loginBtn = document.getElementById('loginBtn');
    const loginText = document.getElementById('loginText');
    const loadingText = document.getElementById('loadingText');
    const apiKeyInput = document.getElementById('apiKey');
    
    if (loading) {
        // 显示加载状态
        loginBtn.disabled = true;
        loginText.classList.add('hidden');
        loadingText.classList.remove('hidden');
        
        if (apiKeyInput) {
            apiKeyInput.disabled = true;
        }
    } else {
        // 恢复正常状态
        loginBtn.disabled = false;
        loginText.classList.remove('hidden');
        loadingText.classList.add('hidden');
        
        if (apiKeyInput) {
            apiKeyInput.disabled = false;
        }
    }
}

// 显示错误信息
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    if (!errorMessage || !errorText) return;
    
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

// 隐藏错误信息
function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    
    if (!errorMessage) return;
    
    errorMessage.classList.add('hidden');
} 