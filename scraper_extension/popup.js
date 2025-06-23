// Estado global da aplicação
let appState = {
    settings: {},
    currentTab: null,
    agents: [],
    connectionStatus: { connected: false, lastCheck: null },
    statistics: { totalRequests: 0, successfulRequests: 0, totalResponseTime: 0 },
    recentHistory: []
};

// Elementos DOM
const elements = {
    // Status e conexão
    statusIndicator: document.getElementById('status-indicator'),
    statusText: document.getElementById('status-text'),
    statusTime: document.getElementById('status-time'),
    statusProgress: document.getElementById('status-progress'),
    
    // Estados
    connectionStatus: document.getElementById('connection-status'),
    errorState: document.getElementById('error-state'),
    mainState: document.getElementById('main-state'),
    errorMessage: document.getElementById('error-message'),
    
    // Informações da página
    pageUrl: document.getElementById('page-url'),
    pageTitle: document.getElementById('page-title'),
    contentSize: document.getElementById('content-size'),
    
    // Configurações
    agentSelect: document.getElementById('agent-select'),
    processingMode: document.getElementById('processing-mode'),
    anonymizeData: document.getElementById('anonymize-data'),
    agentCount: document.getElementById('agent-count'),
    
    // Ações
    saveButton: document.getElementById('save-button'),
    saveSpinner: document.getElementById('save-spinner'),
    saveIcon: document.getElementById('save-icon'),
    saveButtonText: document.getElementById('save-button-text'),
    analyzeBtn: document.getElementById('analyze-btn'),
    dashboardBtn: document.getElementById('dashboard-btn'),
    
    // Botões de controle
    refreshBtn: document.getElementById('refresh-btn'),
    settingsBtn: document.getElementById('settings-btn'),
    retryBtn: document.getElementById('retry-btn'),
    clearHistory: document.getElementById('clear-history'),
    
    // Estatísticas
    statRequests: document.getElementById('stat-requests'),
    statSuccess: document.getElementById('stat-success'),
    statTime: document.getElementById('stat-time'),
    
    // Histórico
    recentHistory: document.getElementById('recent-history'),
    
    // Links
    helpLink: document.getElementById('help-link'),
    settingsLink: document.getElementById('settings-link'),
    
    // Toast
    successToast: document.getElementById('success-toast')
};

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
    await loadSettings();
    await loadCurrentTab();
    await checkConnection();
    await loadAgents();
    loadStatistics();
    loadRecentHistory();
    setupEventListeners();
    applyTheme();
});

// Carregar configurações
async function loadSettings() {
    try {
        const result = await chrome.storage.sync.get([
            'apiUrl', 'streamlitUrl', 'defaultAgent', 'processingMode', 
            'anonymizeData', 'theme', 'showNotifications', 'timeout',
            'totalRequests', 'successfulRequests', 'totalResponseTime'
        ]);
        
        appState.settings = {
            apiUrl: result.apiUrl || 'http://192.168.8.4:5000',
            streamlitUrl: result.streamlitUrl || 'http://localhost:8501',
            defaultAgent: result.defaultAgent || '',
            processingMode: result.processingMode || 'auto',
            anonymizeData: result.anonymizeData || false,
            theme: result.theme || 'dark',
            showNotifications: result.showNotifications || true,
            timeout: result.timeout || 30
        };
        
        appState.statistics = {
            totalRequests: result.totalRequests || 0,
            successfulRequests: result.successfulRequests || 0,
            totalResponseTime: result.totalResponseTime || 0
        };
        
        // Aplicar configurações na UI
        if (elements.processingMode) {
            elements.processingMode.value = appState.settings.processingMode;
        }
        if (elements.anonymizeData) {
            elements.anonymizeData.checked = appState.settings.anonymizeData;
        }
        
        console.log('Configurações carregadas:', appState.settings);
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        showError('Erro ao carregar configurações da extensão');
    }
}

// Carregar informações da aba atual
async function loadCurrentTab() {
    try {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        appState.currentTab = tabs[0];
        
        if (!appState.currentTab?.url || !appState.currentTab.url.startsWith('http')) {
            throw new Error('Página atual não é uma URL válida para captura');
        }
        
        // Atualizar UI com informações da página
        if (elements.pageUrl) {
            elements.pageUrl.textContent = appState.currentTab.url;
            elements.pageUrl.title = appState.currentTab.url;
        }
        if (elements.pageTitle) {
            elements.pageTitle.textContent = appState.currentTab.title || 'Página sem título';
            elements.pageTitle.title = appState.currentTab.title || 'Página sem título';
        }
        
        // Calcular tamanho estimado do conteúdo
        try {
            const results = await chrome.scripting.executeScript({
                target: { tabId: appState.currentTab.id },
                function: () => {
                    const content = document.body?.innerText || '';
                    return Math.round(new Blob([content]).size / 1024);
                }
            });
            
            if (elements.contentSize && results[0]?.result) {
                elements.contentSize.textContent = `${results[0].result} KB`;
            }
        } catch (error) {
            console.log('Não foi possível calcular o tamanho do conteúdo:', error);
            if (elements.contentSize) {
                elements.contentSize.textContent = 'N/A';
            }
        }
        
    } catch (error) {
        console.error('Erro ao carregar informações da aba:', error);
        showError(error.message);
    }
}

// Verificar conexão com a API
async function checkConnection() {
    const startTime = Date.now();
    
    try {
        updateConnectionStatus('checking', 'Verificando conexão...');
        
        const response = await fetch(`${appState.settings.apiUrl}/api/v1/extension/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            signal: AbortSignal.timeout(appState.settings.timeout * 1000)
        });
        
        const responseTime = Date.now() - startTime;
        
        if (response.ok) {
            const data = await response.json();
            appState.connectionStatus = {
                connected: true,
                lastCheck: new Date(),
                responseTime,
                version: data.version || 'N/A'
            };
            
            updateConnectionStatus('connected', 'Conectado', `${responseTime}ms`);
            showMainState();
            
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
    } catch (error) {
        appState.connectionStatus = {
            connected: false,
            lastCheck: new Date(),
            error: error.message
        };
        
        updateConnectionStatus('error', 'Falha na conexão');
        showError(error.message);
        
        console.error('Erro na conexão:', error);
    }
}

// Atualizar status de conexão na UI
function updateConnectionStatus(status, text, time = '') {
    if (!elements.statusIndicator || !elements.statusText) return;
    
    switch (status) {
        case 'checking':
            elements.statusIndicator.innerHTML = `
                <div class="spinner-border spinner-border-sm text-warning" role="status">
                    <span class="visually-hidden">Verificando...</span>
                </div>
            `;
            elements.statusProgress.style.width = '50%';
            elements.statusProgress.className = 'progress-bar bg-warning';
            break;
            
        case 'connected':
            elements.statusIndicator.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
            elements.statusProgress.style.width = '100%';
            elements.statusProgress.className = 'progress-bar bg-success';
            break;
            
        case 'error':
            elements.statusIndicator.innerHTML = '<i class="bi bi-x-circle-fill text-danger"></i>';
            elements.statusProgress.style.width = '100%';
            elements.statusProgress.className = 'progress-bar bg-danger';
            break;
    }
    
    elements.statusText.textContent = text;
    if (elements.statusTime && time) {
        elements.statusTime.textContent = time;
    }
}

// Carregar agentes disponíveis
async function loadAgents() {
    try {
        const response = await fetch(`${appState.settings.apiUrl}/agents`, {
            headers: { 'Content-Type': 'application/json' },
            signal: AbortSignal.timeout(appState.settings.timeout * 1000)
        });
        
        if (response.ok) {
            const data = await response.json();
            appState.agents = data.agents || [];
            
            // Atualizar select de agentes
            if (elements.agentSelect) {
                elements.agentSelect.innerHTML = `
                    <option value="">Selecione um agente...</option>
                    ${appState.agents.map(agent => `
                        <option value="${agent.id}" ${agent.id === appState.settings.defaultAgent ? 'selected' : ''}>
                            ${agent.name} (${agent.type})
                        </option>
                    `).join('')}
                `;
            }
            
            // Atualizar contador
            if (elements.agentCount) {
                elements.agentCount.textContent = `${appState.agents.length} agentes disponíveis`;
            }
            
        } else {
            throw new Error(`Erro ao carregar agentes: ${response.statusText}`);
        }
        
    } catch (error) {
        console.error('Erro ao carregar agentes:', error);
        if (elements.agentSelect) {
            elements.agentSelect.innerHTML = '<option value="">Erro ao carregar agentes</option>';
        }
        if (elements.agentCount) {
            elements.agentCount.textContent = 'Erro ao carregar agentes';
        }
    }
}

// Capturar página
async function capturePage() {
    const agentId = elements.agentSelect?.value;
    if (!agentId) {
        showToast('Por favor, selecione um agente', 'warning');
        return;
    }
    
    if (!appState.currentTab?.url) {
        showToast('Nenhuma página válida para capturar', 'danger');
        return;
    }
    
    setButtonState('saving', true);
    const startTime = Date.now();
    
    try {
        const payload = {
            agent_id: agentId,
            url: appState.currentTab.url,
            title: appState.currentTab.title,
            processing_mode: elements.processingMode?.value || 'auto',
            anonymize_data: elements.anonymizeData?.checked || false
        };
        
        const response = await fetch(`${appState.settings.apiUrl}/api/v1/extension/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: AbortSignal.timeout(appState.settings.timeout * 1000)
        });
        
        const responseTime = Date.now() - startTime;
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Atualizar estatísticas
            await updateStatistics(true, responseTime);
            
            // Adicionar ao histórico
            addToHistory({
                url: appState.currentTab.url,
                title: appState.currentTab.title,
                agent: appState.agents.find(a => a.id === agentId)?.name || agentId,
                timestamp: new Date(),
                success: true
            });
            
            setButtonState('success', false);
            showToast('Página capturada com sucesso!', 'success');
            
            // Resetar botão após 2 segundos
            setTimeout(() => setButtonState('default', false), 2000);
            
        } else {
            throw new Error(result.error || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('Erro ao capturar página:', error);
        await updateStatistics(false, Date.now() - startTime);
        
        addToHistory({
            url: appState.currentTab.url,
            title: appState.currentTab.title,
            agent: appState.agents.find(a => a.id === agentId)?.name || agentId,
            timestamp: new Date(),
            success: false,
            error: error.message
        });
        
        setButtonState('error', false);
        showToast(`Erro: ${error.message}`, 'danger');
        
        // Resetar botão após 3 segundos
        setTimeout(() => setButtonState('default', false), 3000);
    }
}

// Analisar página
async function analyzePage() {
    if (!appState.currentTab?.url) {
        showToast('Nenhuma página para analisar', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${appState.settings.apiUrl}/api/v1/extension/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: appState.currentTab.url }),
            signal: AbortSignal.timeout(appState.settings.timeout * 1000)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showToast(`Análise: ${result.analysis.summary}`, 'info');
        } else {
            throw new Error(result.error || 'Erro na análise');
        }
        
    } catch (error) {
        console.error('Erro ao analisar página:', error);
        showToast(`Erro na análise: ${error.message}`, 'danger');
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Botões principais
    if (elements.saveButton) elements.saveButton.addEventListener('click', capturePage);
    if (elements.analyzeBtn) elements.analyzeBtn.addEventListener('click', analyzePage);
    if (elements.dashboardBtn) elements.dashboardBtn.addEventListener('click', openDashboard);
    
    // Botões de controle
    if (elements.refreshBtn) elements.refreshBtn.addEventListener('click', refresh);
    if (elements.settingsBtn) elements.settingsBtn.addEventListener('click', openSettings);
    if (elements.retryBtn) elements.retryBtn.addEventListener('click', checkConnection);
    if (elements.clearHistory) elements.clearHistory.addEventListener('click', clearHistory);
    
    // Links
    if (elements.settingsLink) elements.settingsLink.addEventListener('click', openSettings);
    if (elements.helpLink) elements.helpLink.addEventListener('click', openHelp);
    
    // Salvar configurações quando mudarem
    if (elements.processingMode) {
        elements.processingMode.addEventListener('change', saveQuickSettings);
    }
    if (elements.anonymizeData) {
        elements.anonymizeData.addEventListener('change', saveQuickSettings);
    }
    if (elements.agentSelect) {
        elements.agentSelect.addEventListener('change', saveQuickSettings);
    }
}

// Salvar configurações rápidas
async function saveQuickSettings() {
    try {
        const newSettings = {
            processingMode: elements.processingMode?.value || appState.settings.processingMode,
            anonymizeData: elements.anonymizeData?.checked || appState.settings.anonymizeData,
            defaultAgent: elements.agentSelect?.value || appState.settings.defaultAgent
        };
        
        await chrome.storage.sync.set(newSettings);
        Object.assign(appState.settings, newSettings);
        
    } catch (error) {
        console.error('Erro ao salvar configurações:', error);
    }
}

// Atualizar estatísticas
async function updateStatistics(success, responseTime) {
    appState.statistics.totalRequests++;
    appState.statistics.totalResponseTime += responseTime;
    
    if (success) {
        appState.statistics.successfulRequests++;
    }
    
    // Salvar no storage
    await chrome.storage.sync.set(appState.statistics);
    
    // Atualizar UI
    loadStatistics();
}

// Carregar e exibir estatísticas
function loadStatistics() {
    if (elements.statRequests) {
        elements.statRequests.textContent = appState.statistics.totalRequests;
    }
    
    const successRate = appState.statistics.totalRequests > 0 
        ? Math.round((appState.statistics.successfulRequests / appState.statistics.totalRequests) * 100)
        : 0;
    if (elements.statSuccess) {
        elements.statSuccess.textContent = successRate + '%';
    }
    
    const avgTime = appState.statistics.totalRequests > 0
        ? Math.round(appState.statistics.totalResponseTime / appState.statistics.totalRequests)
        : 0;
    if (elements.statTime) {
        elements.statTime.textContent = avgTime + 'ms';
    }
}

// Gerenciar histórico
function addToHistory(entry) {
    appState.recentHistory.unshift(entry);
    if (appState.recentHistory.length > 10) {
        appState.recentHistory = appState.recentHistory.slice(0, 10);
    }
    
    // Salvar no storage
    chrome.storage.local.set({ recentHistory: appState.recentHistory });
    
    // Atualizar UI
    updateHistoryUI();
}

function loadRecentHistory() {
    chrome.storage.local.get(['recentHistory'], (result) => {
        appState.recentHistory = result.recentHistory || [];
        updateHistoryUI();
    });
}

function updateHistoryUI() {
    if (!elements.recentHistory) return;
    
    if (appState.recentHistory.length === 0) {
        elements.recentHistory.innerHTML = '<div class="text-center text-muted small">Nenhum histórico ainda</div>';
        return;
    }
    
    elements.recentHistory.innerHTML = appState.recentHistory.map(entry => `
        <div class="border-bottom pb-1 mb-1">
            <div class="d-flex align-items-center justify-content-between">
                <div class="flex-grow-1">
                    <div class="small fw-bold text-truncate">${entry.title}</div>
                    <div class="small text-muted text-truncate">${entry.agent}</div>
                </div>
                <div class="text-end">
                    <i class="bi bi-${entry.success ? 'check-circle-fill text-success' : 'x-circle-fill text-danger'}"></i>
                    <div class="small text-muted">${formatTime(entry.timestamp)}</div>
                </div>
            </div>
        </div>
    `).join('');
}

function clearHistory() {
    if (confirm('Limpar todo o histórico?')) {
        appState.recentHistory = [];
        chrome.storage.local.remove(['recentHistory']);
        updateHistoryUI();
        showToast('Histórico limpo', 'info');
    }
}

// Funções utilitárias
function setButtonState(state, loading) {
    if (!elements.saveButton) return;
    
    elements.saveButton.disabled = loading;
    if (elements.saveSpinner) {
        elements.saveSpinner.classList.toggle('d-none', !loading);
    }
    
    switch (state) {
        case 'saving':
            if (elements.saveIcon) elements.saveIcon.className = 'bi bi-arrow-down-circle me-2';
            if (elements.saveButtonText) elements.saveButtonText.textContent = 'Capturando...';
            elements.saveButton.className = 'btn btn-warning';
            break;
            
        case 'success':
            if (elements.saveIcon) elements.saveIcon.className = 'bi bi-check-circle-fill me-2';
            if (elements.saveButtonText) elements.saveButtonText.textContent = 'Sucesso!';
            elements.saveButton.className = 'btn btn-success';
            break;
            
        case 'error':
            if (elements.saveIcon) elements.saveIcon.className = 'bi bi-x-circle-fill me-2';
            if (elements.saveButtonText) elements.saveButtonText.textContent = 'Erro';
            elements.saveButton.className = 'btn btn-danger';
            break;
            
        default:
            if (elements.saveIcon) elements.saveIcon.className = 'bi bi-download me-2';
            if (elements.saveButtonText) elements.saveButtonText.textContent = 'Capturar Página';
            elements.saveButton.className = 'btn btn-primary';
            break;
    }
}

function showMainState() {
    if (elements.connectionStatus) elements.connectionStatus.classList.remove('d-none');
    if (elements.errorState) elements.errorState.classList.add('d-none');
    if (elements.mainState) elements.mainState.classList.remove('d-none');
}

function showError(message) {
    if (elements.connectionStatus) elements.connectionStatus.classList.remove('d-none');
    if (elements.errorState) {
        elements.errorState.classList.remove('d-none');
        if (elements.errorMessage) {
            elements.errorMessage.textContent = message;
        }
    }
    if (elements.mainState) elements.mainState.classList.add('d-none');
}

function showToast(message, type = 'info') {
    if (appState.settings.showNotifications && elements.successToast) {
        const toast = elements.successToast;
        const body = toast.querySelector('.toast-body');
        if (body) body.textContent = message;
        
        // Atualizar cor baseada no tipo
        const header = toast.querySelector('.toast-header');
        if (header) {
            const icon = header.querySelector('i');
            if (icon) {
                icon.className = `bi bi-${getIconForType(type)} text-${type} me-2`;
            }
        }
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle-fill',
        danger: 'x-circle-fill',
        warning: 'exclamation-triangle-fill',
        info: 'info-circle-fill'
    };
    return icons[type] || 'info-circle-fill';
}

function formatTime(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    if (diff < 60000) return 'agora';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
    return `${Math.floor(diff / 86400000)}d`;
}

function applyTheme() {
    document.documentElement.setAttribute('data-bs-theme', appState.settings.theme);
}

// Ações de navegação
function openSettings(e) {
    e?.preventDefault();
    chrome.runtime.openOptionsPage();
}

function openDashboard() {
    chrome.tabs.create({ url: appState.settings.streamlitUrl });
}

function openHelp(e) {
    e?.preventDefault();
    chrome.tabs.create({ url: 'https://github.com/jessefreitas/rag_python/wiki' });
}

async function refresh() {
    await loadSettings();
    await loadCurrentTab();
    await checkConnection();
    await loadAgents();
    loadStatistics();
    showToast('Interface atualizada', 'success');
} 