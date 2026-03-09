/**
 * Soft Keyboard for bk-robot
 * Touch-friendly virtual keyboard for text input
 */

class SoftKeyboard {
    constructor(options = {}) {
        this.options = {
            autoShow: true,
            enableToggle: true,
            ...options
        };

        this.isShift = false;
        this.isCaps = false;
        this.currentInput = null;
        this.isVisible = false;
        this.currentSymbolSet = 'general'; // general, url, programming
        
        // Consolidated 4-row keyboard layout
        this.layout = {
            name: '虚拟键盘',
            rows: [
                // Row 1: Numbers and backspace (equal width buttons)
                ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', { text: '⌫', class: 'backspace', action: 'backspace' }],
                // Row 2: QWERTY top and middle rows combined
                ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                // Row 3: QWERTY bottom row with shift and symbols
                [{ text: '⇧', class: 'shift', action: 'shift' }, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', { text: '空格', class: 'space', action: 'space' }],
                // Row 4: Dynamic symbol row (changes based on context)
                this.getSymbolRow('general')
            ]
        };

        this.init();
    }

    init() {
        this.createKeyboard();
        this.setupEventListeners();
        this.setupInputDetection();
        
        if (this.options.enableToggle) {
            this.createToggleButton();
        }
    }

    // Get appropriate symbol row based on context (removed :// key and space key)
    getSymbolRow(symbolSet) {
        switch(symbolSet) {
            case 'url':
                return [
                    { text: '/', class: 'symbol', action: 'insert:/' },
                    { text: '?', class: 'symbol', action: 'insert:?' },
                    { text: '=', class: 'symbol', action: 'insert:=' },
                    { text: '&', class: 'symbol', action: 'insert:&' },
                    { text: '@', class: 'symbol', action: 'insert:@' },
                    { text: ':', class: 'symbol', action: 'insert::' },
                    { text: '-', class: 'symbol', action: 'insert:-' },
                    { text: '_', class: 'symbol', action: 'insert:_' },
                    { text: '.', class: 'symbol', action: 'insert:.' }
                ];
            case 'programming':
                return [
                    { text: '{', class: 'symbol', action: 'insert:{' },
                    { text: '}', class: 'symbol', action: 'insert:}' },
                    { text: '[', class: 'symbol', action: 'insert:[' },
                    { text: ']', class: 'symbol', action: 'insert:]' },
                    { text: '(', class: 'symbol', action: 'insert:(' },
                    { text: ')', class: 'symbol', action: 'insert:)' },
                    { text: '<', class: 'symbol', action: 'insert:<' },
                    { text: '>', class: 'symbol', action: 'insert:>' },
                    { text: '|', class: 'symbol', action: 'insert:|' }
                ];
            case 'general':
            default:
                return [
                    { text: '!', class: 'symbol', action: 'insert:!' },
                    { text: '@', class: 'symbol', action: 'insert:@' },
                    { text: '#', class: 'symbol', action: 'insert:#' },
                    { text: '$', class: 'symbol', action: 'insert:$' },
                    { text: '%', class: 'symbol', action: 'insert:%' },
                    { text: '&', class: 'symbol', action: 'insert:&' },
                    { text: '*', class: 'symbol', action: 'insert:*' },
                    { text: '-', class: 'symbol', action: 'insert:-' },
                    { text: '_', class: 'symbol', action: 'insert:_' }
                ];
        }
    }

    createKeyboard() {
        // Create keyboard container without title bar
        this.container = document.createElement('div');
        this.container.className = 'soft-keyboard-container';
        this.container.innerHTML = `
            <div class="keyboard-rows" id="keyboardRows"></div>
        `;

        document.body.appendChild(this.container);
        this.rowsContainer = document.getElementById('keyboardRows');
        
        this.renderLayout();
    }

    createToggleButton() {
        this.toggleButton = document.createElement('button');
        this.toggleButton.className = 'keyboard-toggle';
        this.toggleButton.innerHTML = '<i class="fas fa-keyboard"></i>';
        this.toggleButton.setAttribute('aria-label', '显示/隐藏键盘');
        this.toggleButton.setAttribute('title', '虚拟键盘');
        
        this.toggleButton.addEventListener('click', () => {
            if (this.isVisible) {
                this.hide();
            } else {
                this.show();
            }
        });

        document.body.appendChild(this.toggleButton);
    }

    renderLayout() {
        if (!this.rowsContainer) return;

        this.rowsContainer.innerHTML = '';
        
        this.layout.rows.forEach(row => {
            const rowElement = document.createElement('div');
            rowElement.className = 'keyboard-row';
            
            row.forEach(key => {
                const keyElement = this.createKeyElement(key);
                rowElement.appendChild(keyElement);
            });
            
            this.rowsContainer.appendChild(rowElement);
        });
    }

    createKeyElement(keyConfig) {
        const keyElement = document.createElement('button');
        keyElement.className = 'keyboard-key';
        
        if (typeof keyConfig === 'string') {
            keyElement.textContent = this.getKeyDisplay(keyConfig);
            keyElement.dataset.action = 'insert';
            keyElement.dataset.value = keyConfig;
        } else {
            keyElement.textContent = keyConfig.text;
            keyElement.classList.add(keyConfig.class);
            keyElement.dataset.action = keyConfig.action;
            
            if (keyConfig.action.startsWith('insert:')) {
                keyElement.dataset.value = keyConfig.action.substring(7);
            }
        }
        
        // Add touch/click events
        keyElement.addEventListener('mousedown', (e) => this.handleKeyPress(e));
        keyElement.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.handleKeyPress(e);
        });
        
        return keyElement;
    }

    getKeyDisplay(key) {
        if (this.isShift || this.isCaps) {
            return key.toUpperCase();
        }
        return key;
    }

    handleKeyPress(event) {
        event.preventDefault();
        const keyElement = event.currentTarget;
        const action = keyElement.dataset.action;
        
        // Visual feedback
        keyElement.classList.add('pressed');
        setTimeout(() => keyElement.classList.remove('pressed'), 100);
        
        // Handle action
        switch (action) {
            case 'insert':
                this.insertText(keyElement.dataset.value);
                break;
            case 'insert:/':
                this.insertText('/');
                break;
            case 'insert:?':
                this.insertText('?');
                break;
            case 'insert:=':
                this.insertText('=');
                break;
            case 'insert:&':
                this.insertText('&');
                break;
            case 'insert:@':
                this.insertText('@');
                break;
            case 'insert::':
                this.insertText(':');
                break;
            case 'insert:!':
                this.insertText('!');
                break;
            case 'insert:#':
                this.insertText('#');
                break;
            case 'insert:$':
                this.insertText('$');
                break;
            case 'insert:%':
                this.insertText('%');
                break;
            case 'insert:*':
                this.insertText('*');
                break;
            case 'insert:-':
                this.insertText('-');
                break;
            case 'insert:_':
                this.insertText('_');
                break;
            case 'insert:{':
                this.insertText('{');
                break;
            case 'insert:}':
                this.insertText('}');
                break;
            case 'insert:[':
                this.insertText('[');
                break;
            case 'insert:]':
                this.insertText(']');
                break;
            case 'insert:(':
                this.insertText('(');
                break;
            case 'insert:)':
                this.insertText(')');
                break;
            case 'insert:<':
                this.insertText('<');
                break;
            case 'insert:>':
                this.insertText('>');
                break;
            case 'insert:|':
                this.insertText('|');
                break;
            case 'insert:.':
                this.insertText('.');
                break;
            case 'backspace':
                this.backspace();
                break;
            case 'space':
                this.insertText(' ');
                break;
            case 'shift':
                this.toggleShift();
                break;
        }
    }

    insertText(text) {
        if (!this.currentInput) return;
        
        const input = this.currentInput;
        const start = input.selectionStart;
        const end = input.selectionEnd;
        const value = input.value;
        
        // Insert text at cursor position
        input.value = value.substring(0, start) + text + value.substring(end);
        
        // Move cursor to after inserted text
        input.selectionStart = input.selectionEnd = start + text.length;
        
        // Trigger input event for React/Vue compatibility
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Reset shift after inserting a character
        if (this.isShift && !this.isCaps) {
            this.isShift = false;
            this.renderLayout();
        }
        
        input.focus();
    }

    backspace() {
        if (!this.currentInput) return;
        
        const input = this.currentInput;
        const start = input.selectionStart;
        const end = input.selectionEnd;
        
        if (start === end && start > 0) {
            // Delete character before cursor
            input.value = input.value.substring(0, start - 1) + input.value.substring(end);
            input.selectionStart = input.selectionEnd = start - 1;
        } else if (start !== end) {
            // Delete selected text
            input.value = input.value.substring(0, start) + input.value.substring(end);
            input.selectionStart = input.selectionEnd = start;
        }
        
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.focus();
    }

    toggleShift() {
        this.isShift = !this.isShift;
        this.renderLayout();
    }

    updateSymbolRow(symbolSet) {
        if (this.currentSymbolSet === symbolSet) return;
        
        this.currentSymbolSet = symbolSet;
        // Update the symbol row (4th row, index 3)
        this.layout.rows[3] = this.getSymbolRow(symbolSet);
        this.renderLayout();
    }

    setupEventListeners() {
        // Hide keyboard when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.isVisible) return;
            
            const isKeyboardClick = this.container.contains(e.target) || 
                                   (this.toggleButton && this.toggleButton.contains(e.target));
            
            if (!isKeyboardClick && !this.isInputElement(e.target)) {
                this.hide();
            }
        });

        // Hide on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isVisible) {
                this.hide();
            }
        });
    }

    setupInputDetection() {
        if (!this.options.autoShow) return;
        
        document.addEventListener('focusin', (e) => {
            if (this.isInputElement(e.target)) {
                this.attachToInput(e.target);
            }
        });
        
        // Also check existing inputs
        setTimeout(() => {
            document.querySelectorAll('input[type="text"], input[type="number"], input[type="password"], textarea').forEach(input => {
                this.prepareInput(input);
            });
        }, 100);
    }

    isInputElement(element) {
        return element.tagName === 'INPUT' || element.tagName === 'TEXTAREA';
    }

    prepareInput(input) {
        input.classList.add('input-with-keyboard');
        
        // Add touch event for mobile
        input.addEventListener('touchstart', () => {
            if (this.options.autoShow) {
                this.attachToInput(input);
            }
        });
    }

    attachToInput(input) {
        this.currentInput = input;
        this.prepareInput(input);
        
        // Determine appropriate layout
        this.determineLayout(input);
        
        // Show keyboard
        this.show();
        
        // Scroll input into view if needed
        setTimeout(() => {
            input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }

    determineLayout(input) {
        const inputType = input.type.toLowerCase();
        const inputName = (input.name || '').toLowerCase();
        const inputId = (input.id || '').toLowerCase();
        
        // Check for URL-related fields
        if (inputName.includes('url') || inputName.includes('host') || inputName.includes('address') ||
            inputId.includes('url') || inputId.includes('host') || inputId.includes('address')) {
            this.updateSymbolRow('url');
            return;
        }
        
        // Check for numeric/programming fields
        if (inputType === 'number' || inputName.includes('port') || inputName.includes('num') ||
            inputId.includes('port') || inputId.includes('num')) {
            this.updateSymbolRow('programming');
            return;
        }
        
        // Default to general symbols
        this.updateSymbolRow('general');
    }

    show() {
        this.container.classList.add('visible');
        this.isVisible = true;
        
        if (this.toggleButton) {
            this.toggleButton.innerHTML = '<i class="fas fa-keyboard"></i>';
            this.toggleButton.classList.remove('hidden');
        }
        
        // Add body class to prevent scrolling issues
        document.body.classList.add('keyboard-visible');
    }

    hide() {
        this.container.classList.remove('visible');
        this.isVisible = false;
        this.currentInput = null;
        
        if (this.toggleButton) {
            this.toggleButton.innerHTML = '<i class="fas fa-keyboard"></i>';
        }
        
        // Remove body class
        document.body.classList.remove('keyboard-visible');
        
        // Reset shift state
        if (this.isShift) {
            this.isShift = false;
            this.renderLayout();
        }
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        
        if (this.toggleButton && this.toggleButton.parentNode) {
            this.toggleButton.parentNode.removeChild(this.toggleButton);
        }
        
        document.body.classList.remove('keyboard-visible');
    }
}

// Global instance
let softKeyboardInstance = null;

function initSoftKeyboard(options = {}) {
    if (!softKeyboardInstance) {
        softKeyboardInstance = new SoftKeyboard(options);
    }
    return softKeyboardInstance;
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initSoftKeyboard();
    });
} else {
    initSoftKeyboard();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SoftKeyboard, initSoftKeyboard };
}

// Global access
window.SoftKeyboard = SoftKeyboard;
window.initSoftKeyboard = initSoftKeyboard;