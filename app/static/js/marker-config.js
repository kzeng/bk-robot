let selectedMarkersOrder = [];
let currentPage = 1;
let pageSize = 20;
let totalPages = 1;
let totalCount = 0;
let currentSearchTerm = '';
let currentFloorFilter = '';
let currentBuildingFilter = '';

function updateSelectedMarkersDisplay() {
    // 确保所有以CD开头的点位在最后
    const cdMarkers = selectedMarkersOrder.filter(marker => {
        const markerName = marker || '';
        return markerName.toUpperCase().startsWith('CD');
    });
    
    const nonCdMarkers = selectedMarkersOrder.filter(marker => {
        const markerName = marker || '';
        return !markerName.toUpperCase().startsWith('CD');
    });
    
    // 重新组合：非CD点位在前，CD点位在后
    selectedMarkersOrder = [...nonCdMarkers, ...cdMarkers];
    
    const container = document.getElementById('selectedMarkersList');
    container.innerHTML = '';
    
    if (selectedMarkersOrder.length === 0) {
        container.textContent = '无';
        return;
    }
    
    selectedMarkersOrder.forEach(marker => {
        const badge = document.createElement('span');
        badge.className = 'marker-badge';
        badge.textContent = marker;
        container.appendChild(badge);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    loadFloorOptions();
    loadMarkerConfigs();

    // 监听checkbox变化
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('marker-checkbox')) {
            const marker = e.target.dataset.markerShort;
            if (e.target.checked) {
                if (!selectedMarkersOrder.includes(marker)) {
                    selectedMarkersOrder.push(marker);
                }
            } else {
                selectedMarkersOrder = selectedMarkersOrder.filter(m => m !== marker);
            }
            updateSelectedMarkersDisplay();
        }
    });

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
                    loadFloorOptions();
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
                    loadFloorOptions();
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
        currentPage = 1;
        loadMarkerConfigs();
    });

    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            currentPage = 1;
            loadMarkerConfigs();
        }
    });

    document.getElementById('pageSizeSelect').addEventListener('change', function(e) {
        pageSize = parseInt(e.target.value, 10);
        currentPage = 1;
        loadMarkerConfigs();
    });

    document.getElementById('floorSelect').addEventListener('change', function(e) {
        const selected = e.target.value;
        if (selected) {
            const parts = selected.split('|');
            currentBuildingFilter = parts[0] || '';
            currentFloorFilter = parts[1] || '';
        } else {
            currentBuildingFilter = '';
            currentFloorFilter = '';
        }
        currentPage = 1;
        selectedMarkersOrder = [];
        updateSelectedMarkersDisplay();
        loadMarkerConfigs();
    });

    document.getElementById('pagePrevButton').addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage -= 1;
            loadMarkerConfigs(true);
        }
    });

    document.getElementById('pageNextButton').addEventListener('click', function() {
        if (currentPage < totalPages) {
            currentPage += 1;
            loadMarkerConfigs(true);
        }
    });

    document.getElementById('scrollTopButton').addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Save button click handler
    document.getElementById('saveButton').addEventListener('click', saveMarkerConfig);
});

// Select all checkbox functionality
document.getElementById('selectAllCheckbox').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.marker-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
        const marker = checkbox.dataset.markerShort;
        if (this.checked) {
            if (!selectedMarkersOrder.includes(marker)) {
                selectedMarkersOrder.push(marker);
            }
        } else {
            selectedMarkersOrder = [];
        }
    });
    updateSelectedMarkersDisplay();
});

// Create task button handler
document.getElementById('createTaskButton').addEventListener('click', function() {
    if (selectedMarkersOrder.length < 2) {
        alert('请至少选择两个点位');
        return;
    }

    // 1. 查询当前楼层点位配置
    const params = new URLSearchParams({ all: '1' });
    if (currentBuildingFilter) params.set('building', currentBuildingFilter);
    if (currentFloorFilter) params.set('floor', currentFloorFilter);
    fetch(`/api/marker-config?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('获取点位配置失败');
            }
            return response.json();
        })
        .then(markerConfigs => {
            const selectedConfigs = markerConfigs.filter(config => selectedMarkersOrder.includes(config.mid_short));
            const selectedFloors = new Set(selectedConfigs.map(config => `${config.building || ''}|${config.floor || ''}`));
            if (selectedFloors.size > 1) {
                throw new Error('盘点任务不允许跨楼层，请只选择同一地图/楼层的点位');
            }
            const selectedFloorKey = selectedFloors.size === 1 ? [...selectedFloors][0] : '';

            // 2. 找出所有以CD开头的点位（不区分大小写）
            let cdMarkers = markerConfigs
                .filter(config => {
                    const markerName = config.mid_short || '';
                    const floorKey = `${config.building || ''}|${config.floor || ''}`;
                    return markerName.toUpperCase().startsWith('CD') && (!selectedFloorKey || floorKey === selectedFloorKey);
                })
                .map(config => config.mid_short)
                .sort(); // 按字母顺序排序

            if (cdMarkers.length === 0) {
                cdMarkers = markerConfigs
                    .filter(config => {
                        const markerName = config.mid_short || '';
                        return markerName.toUpperCase().startsWith('CD');
                    })
                    .map(config => config.mid_short)
                    .sort();
            }
            
            // 3. 如果没有任何CD点位，使用默认的'CD'
            if (cdMarkers.length === 0) {
                cdMarkers.push('CD');
            }
            
            // 4. 去重：找出已选中的CD点位
            const existingCdMarkers = selectedMarkersOrder.filter(marker => {
                const markerName = marker || '';
                return markerName.toUpperCase().startsWith('CD');
            });
            
            // 5. 添加未选中的CD点位到末尾
            cdMarkers.forEach(cdMarker => {
                if (!existingCdMarkers.includes(cdMarker)) {
                    selectedMarkersOrder.push(cdMarker);
                }
            });
            
            // 6. 更新显示
            updateSelectedMarkersDisplay();
            
            // 7. 创建任务
            const taskData = {
                marker: selectedMarkersOrder.join(','),
                action: 0,
                description: ''
            };
            
            return fetch('/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(taskData)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('创建任务请求失败');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'OK') {
                window.location.href = '/tasks';
            } else {
                alert('创建任务失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error creating task:', error);
            alert('创建任务失败: ' + error.message);
        });
});

function updatePageControls() {
    document.getElementById('pagePrevButton').disabled = currentPage <= 1;
    document.getElementById('pageNextButton').disabled = currentPage >= totalPages;
}

function updateSelectAllState() {
    const checkboxes = document.querySelectorAll('.marker-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');

    if (checkboxes.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }

    const checkedCount = Array.from(checkboxes).filter(checkbox => checkbox.checked).length;
    selectAllCheckbox.checked = checkedCount === checkboxes.length;
    selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
}

function loadFloorOptions() {
    fetch('/api/marker-config/floors')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('floorSelect');
            if (!select) return;
            const previous = select.value;
            select.innerHTML = '<option value="">全部地图</option>';
            (data.floors || []).forEach(item => {
                const option = document.createElement('option');
                option.value = `${item.building || ''}|${item.floor || ''}`;
                option.textContent = `${item.building ? item.building + ' / ' : ''}${item.floor}`;
                select.appendChild(option);
            });
            if ([...select.options].some(option => option.value === previous)) {
                select.value = previous;
            }
        })
        .catch(error => console.error('Error loading floors:', error));
}

function renderPagination() {
    const ul = document.getElementById('markerPagination');
    const summary = document.getElementById('markerPaginationSummary');
    ul.innerHTML = '';

    if (totalCount === 0) {
        summary.textContent = '当前没有点位数据';
        updatePageControls();
        return;
    }

    summary.textContent = `第 ${currentPage} / ${totalPages} 页，共 ${totalCount} 条点位`;

    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);
    if (currentPage <= 3) {
        endPage = Math.min(maxVisiblePages, totalPages);
    } else if (currentPage >= totalPages - 2) {
        startPage = Math.max(1, totalPages - maxVisiblePages + 1);
    }

    const addPageButton = (label, targetPage, options = {}) => {
        const li = document.createElement('li');
        li.className = 'page-item';
        if (options.disabled) {
            li.classList.add('disabled');
        }
        if (options.active) {
            li.classList.add('active');
        }

        const link = document.createElement(options.disabled ? 'span' : 'a');
        link.className = 'page-link';
        link.textContent = label;
        if (!options.disabled) {
            link.href = '#';
            link.addEventListener('click', function(e) {
                e.preventDefault();
                if (targetPage === currentPage) {
                    return;
                }
                currentPage = targetPage;
                loadMarkerConfigs(true);
            });
        }
        li.appendChild(link);
        ul.appendChild(li);
    };

    addPageButton('上一页', currentPage - 1, { disabled: currentPage === 1 });

    if (startPage > 1) {
        addPageButton('1', 1);
        if (startPage > 2) {
            addPageButton('...', currentPage, { disabled: true });
        }
    }

    for (let pageNumber = startPage; pageNumber <= endPage; pageNumber += 1) {
        addPageButton(String(pageNumber), pageNumber, { active: pageNumber === currentPage });
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            addPageButton('...', currentPage, { disabled: true });
        }
        addPageButton(String(totalPages), totalPages);
    }

    addPageButton('下一页', currentPage + 1, { disabled: currentPage === totalPages });
    updatePageControls();
}

function loadMarkerConfigs(shouldScrollIntoView = false) {
    currentSearchTerm = document.getElementById('searchInput').value.trim();
    const status = document.getElementById('markerConfigStatus');
    status.textContent = '正在加载点位数据...';

    const params = new URLSearchParams({
        search: currentSearchTerm,
        page: String(currentPage),
        size: String(pageSize)
    });
    if (currentBuildingFilter) params.set('building', currentBuildingFilter);
    if (currentFloorFilter) params.set('floor', currentFloorFilter);

    fetch(`/api/marker-config?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('markerConfigTable');
            tbody.innerHTML = '';

            const configs = data.items || [];
            const pagination = data.pagination || {};
            currentPage = pagination.page || currentPage;
            pageSize = pagination.size || pageSize;
            totalPages = pagination.pages || 1;
            totalCount = pagination.total || 0;

            document.getElementById('pageSizeSelect').value = String(pageSize);

            if (configs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="16" class="empty-state">没有找到匹配的点位，请调整搜索条件。</td></tr>';
            }

            configs.forEach(config => {
                const tr = document.createElement('tr');
                const isChecked = selectedMarkersOrder.includes(config.mid_short);
                tr.innerHTML = `
                    <td><input type="checkbox" class="marker-checkbox" data-marker-short="${config.mid_short}" ${isChecked ? 'checked' : ''}></td>
                    <td>${config.id}</td>
                    <td>${config.building ? config.building + ' / ' : ''}${config.floor || ''}</td>
                    <td>${config.poi_name || ''}</td>
                    <td>${config.mid}</td>
                    
                    <td>${config.mid_short}</td>
                    <td>${config.x}</td>
                    <td>${config.y}</td>
                    <td>${config.w}</td>
                    <td>${config.h}</td>
                    
                    <td>${config.mid2 || ''}</td>
                    <td>${config.x2}</td>
                    <td>${config.y2}</td>
                    <td>${config.w2}</td>
                    <td>${config.h2}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editMarkerConfig(${JSON.stringify(config).replace(/"/g, '&quot;')})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        &nbsp;&nbsp;&nbsp;
                        <button class="btn btn-sm btn-danger" onclick="deleteMarkerConfig(${config.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            const startIndex = totalCount === 0 ? 0 : ((currentPage - 1) * pageSize) + 1;
            const endIndex = Math.min(currentPage * pageSize, totalCount);
            status.textContent = totalCount === 0
                ? '当前没有可显示的点位数据'
                : `当前显示第 ${startIndex} - ${endIndex} 条，共 ${totalCount} 条点位`;

            renderPagination();
            updateSelectAllState();

            if (shouldScrollIntoView) {
                document.getElementById('markerTableViewport').scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        })
        .catch(error => {
            console.error('Error loading marker configs:', error);
            document.getElementById('markerConfigStatus').textContent = '加载点位配置失败';
            alert('加载点位配置失败');
        });
}

function editMarkerConfig(config) {
    document.getElementById('configId').value = config.id;
    document.getElementById('mid').value = config.mid;
    document.getElementById('mid2').value = config.mid2 || '';
    document.getElementById('building').value = config.building || '';
    document.getElementById('floor').value = config.floor || '';
    document.getElementById('poiName').value = config.poi_name || '';
    document.getElementById('poiId').value = config.poi_id || '';
    document.getElementById('midShort').value = config.mid_short;
    document.getElementById('x').value = config.x;
    document.getElementById('y').value = config.y;
    document.getElementById('w').value = config.w;
    document.getElementById('h').value = config.h;
    document.getElementById('x2').value = config.x2 || 0;
    document.getElementById('y2').value = config.y2 || 0;
    document.getElementById('w2').value = config.w2 || 0;
    document.getElementById('h2').value = config.h2 || 0;
    
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
        mid2: document.getElementById('mid2').value,
        building: document.getElementById('building').value,
        floor: document.getElementById('floor').value,
        poi_name: document.getElementById('poiName').value,
        poi_id: document.getElementById('poiId').value,
        mid_short: document.getElementById('midShort').value,
        x: parseInt(document.getElementById('x').value),
        y: parseInt(document.getElementById('y').value),
        w: parseInt(document.getElementById('w').value),
        h: parseInt(document.getElementById('h').value),
        x2: parseInt(document.getElementById('x2').value),
        y2: parseInt(document.getElementById('y2').value),
        w2: parseInt(document.getElementById('w2').value),
        h2: parseInt(document.getElementById('h2').value)
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
