document.addEventListener('DOMContentLoaded', function() {
    loadMarkerConfigs();

    // 同步点位按钮点击事件
    document.getElementById('syncMarkersButton').addEventListener('click', function() {
        if (confirm('确定要从机器人同步点位配置吗？这将会覆盖现有配置。')) {
            fetch('/api/marker-config/sync', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'OK') {
                    alert(data.message);
                    loadMarkerConfigs();
                } else {
                    alert('同步失败：' + data.message);
                }
            })
            .catch(error => {
                console.error('Error syncing markers:', error);
                alert('同步点位失败');
            });
        }
    });

    // 清空点位按钮点击事件
    document.getElementById('clearMarkersButton').addEventListener('click', function() {
        if (confirm('确定要清空所有点位配置吗？此操作不可恢复！')) {
            fetch('/api/marker-config/clear', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'OK') {
                    alert(data.message);
                    loadMarkerConfigs();
                } else {
                    alert('清空失败：' + data.message);
                }
            })
            .catch(error => {
                console.error('Error clearing markers:', error);
                alert('清空点位失败');
            });
        }
    });

    // Search functionality
    document.getElementById('searchButton').addEventListener('click', function() {
        loadMarkerConfigs();
    });

    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loadMarkerConfigs();
        }
    });

    // Save button click handler
    document.getElementById('saveButton').addEventListener('click', saveMarkerConfig);
});

// Select all checkbox functionality
document.getElementById('selectAllCheckbox').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.marker-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
});

// Create task button handler
document.getElementById('createTaskButton').addEventListener('click', function() {
    const selectedMarkers = [];
    document.querySelectorAll('.marker-checkbox:checked').forEach(checkbox => {
        selectedMarkers.push(checkbox.dataset.markerShort);
    });

    if (selectedMarkers.length < 2) {
        alert('请至少选择两个点位');
        return;
    }

    const taskData = {
        marker: selectedMarkers.join(','),
        action: 0,
        description: ''
    };

    fetch('/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData)
    })
    .then(response => response.json())
    .then(data => {
            if (data.status === 'OK') {
                window.location.href = '/tasks';
            } else {
            alert('创建任务失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error creating task:', error);
        alert('创建任务失败');
    });
});

function loadMarkerConfigs() {
    const searchTerm = document.getElementById('searchInput').value;
    fetch(`/api/marker-config?search=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('markerConfigTable');
            tbody.innerHTML = '';
            
            data.forEach(config => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><input type="checkbox" class="marker-checkbox" data-marker-short="${config.mid_short}"></td>
                    <td>${config.id}</td>
                    <td>${config.mid}</td>
                    <td>${config.mid_short}</td>
                    <td>${config.x}</td>
                    <td>${config.y}</td>
                    <td>${config.w}</td>
                    <td>${config.h}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editMarkerConfig(${JSON.stringify(config).replace(/"/g, '&quot;')})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteMarkerConfig(${config.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error loading marker configs:', error);
            alert('加载点位配置失败');
        });
}

function editMarkerConfig(config) {
    document.getElementById('configId').value = config.id;
    document.getElementById('mid').value = config.mid;
    document.getElementById('midShort').value = config.mid_short;
    document.getElementById('x').value = config.x;
    document.getElementById('y').value = config.y;
    document.getElementById('w').value = config.w;
    document.getElementById('h').value = config.h;
    
    document.getElementById('markerConfigModalLabel').textContent = '编辑点位';
    const modal = new bootstrap.Modal(document.getElementById('markerConfigModal'));
    modal.show();
}

function clearForm() {
    document.getElementById('markerConfigForm').reset();
    document.getElementById('configId').value = '';
    document.getElementById('markerConfigModalLabel').textContent = '新增点位';
}

function saveMarkerConfig() {
    const id = document.getElementById('configId').value;
    const data = {
        mid: document.getElementById('mid').value,
        mid_short: document.getElementById('midShort').value,
        x: parseInt(document.getElementById('x').value),
        y: parseInt(document.getElementById('y').value),
        w: parseInt(document.getElementById('w').value),
        h: parseInt(document.getElementById('h').value)
    };

    const url = id ? `/api/marker-config/${id}` : '/api/marker-config';
    const method = id ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        loadMarkerConfigs();
        const modal = bootstrap.Modal.getInstance(document.getElementById('markerConfigModal'));
        modal.hide();
        clearForm();
    })
    .catch(error => {
        console.error('Error saving marker config:', error);
        alert('保存点位配置失败');
    });
}

function deleteMarkerConfig(id) {
    if (!confirm('确定要删除这个点位配置吗？')) {
        return;
    }

    fetch(`/api/marker-config/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        loadMarkerConfigs();
    })
    .catch(error => {
        console.error('Error deleting marker config:', error);
        alert('删除点位配置失败');
    });
}

// Reset form when modal is closed
document.getElementById('markerConfigModal').addEventListener('hidden.bs.modal', clearForm);
