document.getElementById('settingsForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // 获取所有表单数据
    const formData = new FormData(e.target);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // 显示加载提示
    showToast('正在保存设置...', 'info');
    
    // 发送设置更新请求
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'OK') {
            showToast(data.message, 'success');
            if (data.reload) {
                // 如果需要重载，等待2秒后刷新页面
                setTimeout(() => {
                    showToast('正在重新加载页面...', 'info');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }, 2000);
            }
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('保存设置失败: ' + error.message, 'error');
    });
});

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastElement);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // 自动移除旧的 toast
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}
