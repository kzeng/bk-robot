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
    panel.style.display = 'block';
    
    // Update panel content
    document.getElementById('taskId').textContent = taskId;
    document.getElementById('action').textContent = task.action === 0 ? '拍照' : '录像';
    document.getElementById('description').textContent = task.description;
    
    // Setup timeline
    const markers = task.marker.split(',');
    const timeline = document.getElementById('timeline');
    timeline.innerHTML = markers.map(m => 
        `<span class="badge bg-secondary marker-badge" data-marker="${m}">${m}</span>`
    ).join('');
    
    // Initialize empty thumbnails
    const thumbnails = document.getElementById('thumbnails');
    thumbnails.innerHTML = Array(4).fill().map(() => 
        `<div class="img-thumbnail placeholder" style="width: 100px; height: 100px; 
          background: #eee; display: inline-flex; align-items: center; justify-content: center;">
            <span class="text-muted">No Image</span>
        </div>`
    ).join('');

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
                    
                    // Update progress bar
                    document.getElementById('progressBar').style.width = `${progress}%`;
                    document.getElementById('currentMarker').textContent = 
                        `正在处理: ${markerName}`;
                    
                    // Highlight current marker
                    document.querySelectorAll('.marker-badge').forEach(badge => {
                        badge.classList.remove('bg-success');
                        if (badge.dataset.marker === markerName) {
                            badge.classList.add('bg-success');
                        }
                    });
                    
                    // Update thumbnails as they come in
                    if (data.photo_path) {
                        const thumbnails = document.getElementById('thumbnails');
                        // Replace first placeholder
                        const placeholders = thumbnails.querySelectorAll('.placeholder');
                        if (placeholders.length > 0) {
                            placeholders[0].outerHTML = 
                                `<img src="${data.photo_path}" class="img-thumbnail" 
                                 style="width: 100px; height: 100px;">`;
                        } else {
                            // If no placeholders left, add to end (max 4)
                            if (thumbnails.children.length < 4) {
                                thumbnails.insertAdjacentHTML('beforeend',
                                    `<img src="${data.photo_path}" class="img-thumbnail" 
                                     style="width: 100px; height: 100px;">`);
                            }
                        }
                    }
                } catch (error) {
                    console.error('处理进度更新失败:', error);
                    document.getElementById('currentMarker').textContent = 
                        '更新进度时出错';
                }
            };
            
            socket.onclose = () => {
                // Final updates when task completes
                document.getElementById('progressBar').style.width = '100%';
                document.getElementById('progressBar').classList.remove('progress-bar-animated');
                document.getElementById('currentMarker').textContent = '任务完成!';
                
                // Update task list
                loadTasks();
            };
        } else {
            throw new Error(result.error || 'Task execution failed');
        }
    } catch (error) {
        console.error('Task failed:', error);
        document.getElementById('progressBar').classList.add('bg-danger');
        document.getElementById('currentMarker').textContent = `错误: ${error.message}`;
    }
}
