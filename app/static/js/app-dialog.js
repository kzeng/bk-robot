(function () {
    let dialogModal = null;
    let dialogElement = null;

    function ensureDialog() {
        if (dialogElement) return dialogElement;

        dialogElement = document.createElement('div');
        dialogElement.className = 'modal fade';
        dialogElement.id = 'appDialogModal';
        dialogElement.tabIndex = -1;
        dialogElement.setAttribute('aria-hidden', 'true');
        dialogElement.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="appDialogTitle">提示</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>
                    </div>
                    <div class="modal-body">
                        <div id="appDialogMessage" style="white-space: pre-wrap;"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="appDialogCancel">取消</button>
                        <button type="button" class="btn btn-primary" id="appDialogOk">确定</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(dialogElement);
        dialogModal = new bootstrap.Modal(dialogElement, {
            backdrop: 'static',
            keyboard: false
        });
        return dialogElement;
    }

    function showDialog(message, options = {}) {
        ensureDialog();

        const title = options.title || '提示';
        const okText = options.okText || '确定';
        const cancelText = options.cancelText || '取消';
        const variant = options.variant || 'primary';
        const showCancel = Boolean(options.showCancel);

        const titleElement = dialogElement.querySelector('#appDialogTitle');
        const messageElement = dialogElement.querySelector('#appDialogMessage');
        const okButton = dialogElement.querySelector('#appDialogOk');
        const cancelButton = dialogElement.querySelector('#appDialogCancel');

        titleElement.textContent = title;
        messageElement.textContent = String(message ?? '');
        okButton.textContent = okText;
        okButton.className = `btn btn-${variant}`;
        cancelButton.textContent = cancelText;
        cancelButton.style.display = showCancel ? '' : 'none';

        return new Promise((resolve) => {
            let settled = false;

            const cleanup = () => {
                okButton.removeEventListener('click', onOk);
                cancelButton.removeEventListener('click', onCancel);
                dialogElement.removeEventListener('hidden.bs.modal', onHidden);
            };

            const settle = (value) => {
                if (settled) return;
                settled = true;
                cleanup();
                resolve(value);
            };

            const onOk = () => {
                dialogModal.hide();
                settle(true);
            };

            const onCancel = () => {
                dialogModal.hide();
                settle(false);
            };

            const onHidden = () => {
                settle(false);
            };

            okButton.addEventListener('click', onOk);
            cancelButton.addEventListener('click', onCancel);
            dialogElement.addEventListener('hidden.bs.modal', onHidden);
            dialogModal.show();
        });
    }

    window.appAlert = function appAlert(message, options = {}) {
        return showDialog(message, {
            title: options.title || '提示',
            okText: options.okText || '确定',
            variant: options.variant || 'primary',
            showCancel: false
        });
    };

    window.appConfirm = function appConfirm(message, options = {}) {
        return showDialog(message, {
            title: options.title || '请确认',
            okText: options.okText || '确定',
            cancelText: options.cancelText || '取消',
            variant: options.variant || 'primary',
            showCancel: true
        });
    };

    window.alert = function alert(message) {
        window.appAlert(message);
    };

    window.confirm = function confirm(message) {
        window.appAlert(`页面仍在调用旧确认接口，请联系维护人员更新此操作。\n\n${message}`, {
            title: '确认弹窗未升级',
            variant: 'warning'
        });
        return false;
    };
}());
