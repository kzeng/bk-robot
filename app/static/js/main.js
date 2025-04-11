function confirmAndRunTask(taskId) {
    if (confirm('Are you sure you want to execute this task?')) {
        runTask(taskId);
    }
}

async function clearLogs() {
    if (!confirm('确定要清空所有日志吗？此操作不可撤销！')) {
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

async function runTask(taskId) {
    // Show confirmation dialog
    if (!confirm('Are you sure you want to execute this task?')) {
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
        if (statusElement) statusElement.innerHTML = '<span class="text-muted" style="font-size: 3em; font-weight: bold;">准备就绪</span>';
    }
    

    try {
        // Execute task
        const response = await fetch(`/api/tasks/${taskId}/run`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            // Setup WebSocket for real-time updates
            const socket = new WebSocket(`ws://${window.location.host}/ws/task/${taskId}`);
            
            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) || {};
                    const currentMarker = data.current_marker || 0;
                    const markerName = data.current_marker_name || '未知标记点';
                    const progress = markers.length > 0 ? 
                        (currentMarker / markers.length) * 100 : 0;
                    
                    // Update status
                    const statusElement = document.getElementById('taskStatus');
                    if (statusElement) {
                        statusElement.innerHTML = '<span class="text-primary" style="font-size: 3em; font-weight: bold;">正在执行</span>';
                    }
                    
                    // Highlight current marker
                    document.querySelectorAll('.marker-badge').forEach(badge => {
                        badge.classList.remove('bg-success');
                        if (badge.dataset.marker === markerName) {
                            badge.classList.add('bg-success');
                        }
                    });
                    
                } catch (error) {
                    console.error('处理进度更新失败:', error);
                }
            };
            
            socket.onclose = () => {
                // Final updates when task completes
                const statusElement = document.getElementById('taskStatus');
                if (statusElement) {
                    statusElement.innerHTML = '<span class="text-success" style="font-size: 3em; font-weight: bold;">已完成</span>';
                }
                
                // Update task list
                loadTasks();
            };
        } else {
            throw new Error(result.error || 'Task execution failed');
        }
    } catch (error) {
        console.error('Task failed:', error);
   
        const statusElement = document.getElementById('taskStatus');
        if (statusElement) {
            statusElement.innerHTML = '<span class="text-warning" style="font-size: 3em; font-weight: bold;">执行失败</span>';
            console.error('Task failed:', error);
        }
    }
}
