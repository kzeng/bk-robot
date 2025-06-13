let statusPollingEnabled = false;
let pollingInterval = null;

// move_status 状态解释映射
const moveStatusMap = {
    'idle': '等待移动指令',
    'running': '正在移动中',
    'succeeded': '移动已完成',
    'failed': '移动已失败',
    'canceled': '移动已取消'
};

// running_status 状态解释映射
const runningStatusMap = {
    'idle': '可接受任务',
    'leave_charging_pile': '离开充电桩',
    'dock_to_charging_pile': '对接充电桩',
    'goto_lift': '前往电梯',
    'wait_lift_unlock': '等待解锁',
    'wait_lift_outside': '等候电梯',
    'enter_lift': '进入电梯',
    'avoid_lift': '避让电梯',
    'take_lift': '乘坐电梯',
    'exit_lift': '正在出梯',
    'back_to_lift': '返回电梯',
    'running': '正常移动中'
};

function formatDateTime(date) {
    const pad = (n) => String(n).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function updateRobotStatus() {
    fetch('/api/robot/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('statusTimestamp').textContent = formatDateTime(new Date());            document.getElementById('moveTarget').textContent = data.move_target || 'N/A';            // Update move status
            const moveStatus = document.getElementById('moveStatus');
            const moveStatusText = data.move_status || 'N/A';
            const moveDesc = data.move_status ? moveStatusMap[data.move_status] : '';            moveStatus.textContent = moveDesc ? 
                `${moveStatusText}/${moveDesc}` : 
                moveStatusText;
            
            // Update running status
            const runningStatus = document.getElementById('runningStatus');
            const runningStatusText = data.running_status || 'N/A';
            const runningDesc = data.running_status ? runningStatusMap[data.running_status] : '';
            runningStatus.textContent = runningDesc ? 
                `${runningStatusText}/${runningDesc}` : 
                runningStatusText;
            
            // Update charge state
            const chargeState = document.getElementById('chargeState');
            chargeState.textContent = data.charge_state ? '充电中' : '未充电';
            chargeState.className = `badge ${data.charge_state ? 'bg-success' : 'bg-secondary'}`;
            
            // Update estop state
            const estopState = document.getElementById('estopState');
            estopState.textContent = data.estop_state ? '急停中' : '正常';
            estopState.className = `badge ${data.estop_state ? 'bg-danger' : 'bg-success'}`;
            
            // Update power percent
            const powerPercent = document.getElementById('powerPercent');
            powerPercent.textContent = `${data.power_percent}%`;
            powerPercent.className = `badge ${data.power_percent > 20 ? 'bg-success' : 'bg-danger'}`;
        })
        .catch(error => console.error('Error fetching robot status:', error));
}

function toggleStatusPolling() {
    statusPollingEnabled = !statusPollingEnabled;
    const toggleButton = document.getElementById('togglePolling');
    const icon = statusPollingEnabled ? 'bi-eye-fill' : 'bi-eye-slash-fill';
    const text = statusPollingEnabled ? '停止状态更新' : '开始状态更新';
    toggleButton.innerHTML = `<i class="bi ${icon} me-1"></i>${text}`;
    toggleButton.className = `btn btn-sm ${statusPollingEnabled ? 'btn-danger' : 'btn-success'}`;
    
    if (statusPollingEnabled) {
        updateRobotStatus();
        pollingInterval = setInterval(updateRobotStatus, 1000);
    } else {
        clearInterval(pollingInterval);
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Default to disabled
    document.getElementById('statusTimestamp').textContent = formatDateTime(new Date());
    // Don't start polling by default
});
