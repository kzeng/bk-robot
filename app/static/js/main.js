async function confirmAndRunTask(taskId) {
    if (await appConfirm('确定要执行此任务吗？')) {
        runTask(taskId);
    }
}

async function clearLogs() {
    if (!await appConfirm('确定要清空所有日志吗？此操作不可撤销！', {
        title: '危险操作',
        okText: '清空',
        variant: 'danger'
    })) {
        return;
    }
    
    try {
        const response = await fetch('/api/task-logs/clear', {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            alert(result.message || '日志已成功清空');
            window.location.reload();
        } else {
            throw new Error('清空日志失败');
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
        alert('清空日志时出错: ' + error.message);
    }
}

async function runTask(taskId) {    // Show confirmation dialog
    if (!await appConfirm('确定要执行此任务吗？')) {
        return;
    }

    // Get task details
    const task = await fetch(`/api/tasks/${taskId}`).then(r => r.json());
    
    // Show task panel
    const panel = document.getElementById('taskPanel');
    if (panel) {
        panel.style.display = 'block';
        
        // Update panel content
        const taskIdElement = document.getElementById('taskId');
        const actionElement = document.getElementById('action');
        const descriptionElement = document.getElementById('description');
        const statusElement = document.getElementById('taskStatus');
        
        if (taskIdElement) taskIdElement.textContent = taskId;
        if (actionElement) actionElement.textContent = task.action === 0 ? '拍照' : '录像';
        if (descriptionElement) descriptionElement.textContent = task.description;
        if (statusElement) statusElement.innerHTML = '<span class="text-muted" style="font-size: 1.1em; font-weight: bold;">准备启动...</span>';
    }
    
    try {
        // Execute task
        const response = await fetch(`/api/tasks/${taskId}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        
        if (result.status !== 'OK') {
            throw new Error(result.message || '任务执行失败');
        }
        
        // Update status to show task is running
        const statusElement = document.getElementById('taskStatus');
        if (statusElement) {
            statusElement.innerHTML = '<span class="text-primary" style="font-size: 1.1em; font-weight: bold;">正在执行</span>';
        }
        
        // Start polling for task status
        pollTaskStatus(taskId);
        
    } catch (error) {
        console.error('Task failed:', error);
        const statusElement = document.getElementById('taskStatus');
        if (statusElement) {
            statusElement.innerHTML = '<span class="text-warning" style="font-size: 1.1em; font-weight: bold;">启动失败</span>';
        }
        alert('任务启动失败: ' + error.message);
    }
}

// 轮询任务状态
async function pollTaskStatus(taskId) {
    const POLL_INTERVAL = 5000; // 每5秒轮询一次
    const MAX_ATTEMPTS = 2160;  // 最多轮询3小时 (2160 * 5秒 = 3小时)
    let attempts = 0;
    
    const statusMap = {
        1: ['进行中', 'text-primary'],
        2: ['已完成', 'text-success'],
        3: ['部分完成', 'text-warning'],
        4: ['执行失败', 'text-danger']
    };
    
    const poll = async () => {
        try {
            const response = await fetch(`/api/tasks/${taskId}/logs`);
            const logs = await response.json();
            
            if (logs && logs.length > 0) {
                const latestLog = logs[0];
                const [statusText, statusClass] = statusMap[latestLog.status] || ['未知', 'text-muted'];
                
                // 更新任务状态显示
                const statusElement = document.getElementById('taskStatus');
                if (statusElement) {
                    statusElement.innerHTML = `<span class="${statusClass}" style="font-size: 1.1em; font-weight: bold;">
                        ${statusText} | 文件数: ${latestLog.file_count}
                    </span>`;
                }
                
                // 如果任务已经完成或失败，停止轮询
                if ([2, 3, 4].includes(latestLog.status)) {
                    // 显示结果消息
                    if (latestLog.status === 2) {
                        alert('任务执行完成！');
                    } else if (latestLog.status === 3) {
                        alert('任务部分完成，请检查日志了解详情');
                    } else {
                        alert('任务执行失败，请检查日志了解详情');
                    }
                    
                    // 刷新任务列表
                    if (typeof loadTasks === 'function') {
                        loadTasks();
                    }
                    return;
                }
                
                // 继续轮询
                if (attempts++ < MAX_ATTEMPTS) {
                    setTimeout(poll, POLL_INTERVAL);
                } else {
                    alert('任务状态轮询超时');
                }
            }
        } catch (error) {
            console.error('轮询任务状态出错:', error);
            const statusElement = document.getElementById('taskStatus');
            if (statusElement) {
                statusElement.innerHTML = '<span class="text-danger" style="font-size: 1.1em; font-weight: bold;">状态查询失败</span>';
            }
        }
    };
    
    // 开始首次轮询
    poll();
}
