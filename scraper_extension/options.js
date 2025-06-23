// Configurações padrão da extensão
const DEFAULT_SETTINGS = {
    // API Configuration
    apiUrl: 'http://192.168.8.4:5000',
    streamlitUrl: 'http://localhost:8501',
    timeout: 30,
    retryAttempts: 3,
    
    // Agent Configuration
    defaultAgent: '',
    processingMode: 'auto',
    autoProcess: true,
    
    // Preferences
    theme: 'dark',
    showNotifications: true,
    showSuccessPopup: true,
    contextMenu: true,
    
    // Privacy & Security
    anonymizeData: false,
    encryptStorage: false,
    clearOnClose: false,
    dataRetention: 30,
    
    // Advanced
    debugMode: false,
    experimentalFeatures: false,
    maxContentLength: 5000,
    customHeaders: '{}',
    
    // Statistics
    totalRequests: 0,
    successfulRequests: 0,
    totalResponseTime: 0,
    lastUpdate: null
};

// Estado global da aplicação
let currentSettings = { ...DEFAULT_SETTINGS };
let availableAgents = [];
let connectionStatus = { connected: false, lastCheck: null };

// Elementos DOM
const elements = {
    // Status
    statusMessage: document.getElementById('status-message'),
    statusIndicator: document.getElementById('status-indicator'),
    statusTitle: document.getElementById('status-title'),
    statusDetails: document.getElementById('status-details'),
    
    // API Configuration
    apiUrl: document.getElementById('api-url'),
    streamlitUrl: document.getElementById('streamlit-url'),
    timeout: document.getElementById('timeout'),
    retryAttempts: document.getElementById('retry-attempts'),
    endpointsList: document.getElementById('endpoints-list'),
    
    // Agent Configuration
    defaultAgent: document.getElementById('default-agent'),
    processingMode: document.getElementById('processing-mode'),
    autoProcess: document.getElementById('auto-process'),
    agentsList: document.getElementById('agents-list'),
    
    // Preferences
    themeInputs: document.querySelectorAll('input[name="theme"]'),
    showNotifications: document.getElementById('show-notifications'),
    showSuccessPopup: document.getElementById('show-success-popup'),
    contextMenu: document.getElementById('context-menu'),
    
    // Privacy
    anonymizeData: document.getElementById('anonymize-data'),
    encryptStorage: document.getElementById('encrypt-storage'),
    clearOnClose: document.getElementById('clear-on-close'),
    dataRetention: document.getElementById('data-retention'),
    
    // Advanced
    debugMode: document.getElementById('debug-mode'),
    experimentalFeatures: document.getElementById('experimental-features'),
    maxContentLength: document.getElementById('max-content-length'),
    customHeaders: document.getElementById('custom-headers'),
    
    // Statistics
    totalRequests: document.getElementById('total-requests'),
    successRate: document.getElementById('success-rate'),
    avgResponseTime: document.getElementById('avg-response-time'),
    lastUpdate: document.getElementById('last-update'),
    
    // Buttons
    testConnection: document.getElementById('test-connection'),
    resetSettings: document.getElementById('reset-settings'),
    saveAll: document.getElementById('save-all'),
    openDashboard: document.getElementById('open-dashboard'),
    viewLogs: document.getElementById('view-logs'),
    exportSettings: document.getElementById('export-settings'),
    importSettings: document.getElementById('import-settings'),
    importFile: document.getElementById('import-file')
};

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
    await loadSettings();
    await checkConnection();
    await loadAgents();
    setupEventListeners();
    updateStatistics();
    applyTheme();
    
    // Verificar conexão periodicamente
    setInterval(checkConnection, 60000); // A cada minuto
});

// Carregar configurações salvas
async function loadSettings() {
    try {
        const result = await chrome.storage.sync.get(Object.keys(DEFAULT_SETTINGS));
        currentSettings = { ...DEFAULT_SETTINGS, ...result };
        
        // Aplicar configurações aos elementos
        if (elements.apiUrl) elements.apiUrl.value = currentSettings.apiUrl;
        if (elements.streamlitUrl) elements.streamlitUrl.value = currentSettings.streamlitUrl;
        if (elements.timeout) elements.timeout.value = currentSettings.timeout;
        if (elements.retryAttempts) elements.retryAttempts.value = currentSettings.retryAttempts;
        
        if (elements.defaultAgent) elements.defaultAgent.value = currentSettings.defaultAgent;
        if (elements.processingMode) elements.processingMode.value = currentSettings.processingMode;
        if (elements.autoProcess) elements.autoProcess.checked = currentSettings.autoProcess;
        
        elements.themeInputs.forEach(input => {
            input.checked = input.value === currentSettings.theme;
        });
        if (elements.showNotifications) elements.showNotifications.checked = currentSettings.showNotifications;
        if (elements.showSuccessPopup) elements.showSuccessPopup.checked = currentSettings.showSuccessPopup;
        if (elements.contextMenu) elements.contextMenu.checked = currentSettings.contextMenu;
        
        if (elements.anonymizeData) elements.anonymizeData.checked = currentSettings.anonymizeData;
        if (elements.encryptStorage) elements.encryptStorage.checked = currentSettings.encryptStorage;
        if (elements.clearOnClose) elements.clearOnClose.checked = currentSettings.clearOnClose;
        if (elements.dataRetention) elements.dataRetention.value = currentSettings.dataRetention;
        
        if (elements.debugMode) elements.debugMode.checked = currentSettings.debugMode;
        if (elements.experimentalFeatures) elements.experimentalFeatures.checked = currentSettings.experimentalFeatures;
        if (elements.maxContentLength) elements.maxContentLength.value = currentSettings.maxContentLength;
        if (elements.customHeaders) elements.customHeaders.value = currentSettings.customHeaders;
        
        if (currentSettings.lastUpdate && elements.lastUpdate) {
            elements.lastUpdate.textContent = new Date(currentSettings.lastUpdate).toLocaleString('pt-BR');
        }
        
        console.log('Configurações carregadas:', currentSettings);
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        showStatus('Erro ao carregar configurações', 'danger');
    }
}

// Salvar todas as configurações
async function saveAllSettings() {
    try {
        // Coletar dados dos formulários
        const newSettings = {
            // API Configuration
            apiUrl: elements.apiUrl?.value?.trim() || currentSettings.apiUrl,
            streamlitUrl: elements.streamlitUrl?.value?.trim() || currentSettings.streamlitUrl,
            timeout: parseInt(elements.timeout?.value) || currentSettings.timeout,
            retryAttempts: parseInt(elements.retryAttempts?.value) || currentSettings.retryAttempts,
            
            // Agent Configuration
            defaultAgent: elements.defaultAgent?.value || currentSettings.defaultAgent,
            processingMode: elements.processingMode?.value || currentSettings.processingMode,
            autoProcess: elements.autoProcess?.checked ?? currentSettings.autoProcess,
            
            // Preferences
            theme: document.querySelector('input[name="theme"]:checked')?.value || currentSettings.theme,
            showNotifications: elements.showNotifications?.checked ?? currentSettings.showNotifications,
            showSuccessPopup: elements.showSuccessPopup?.checked ?? currentSettings.showSuccessPopup,
            contextMenu: elements.contextMenu?.checked ?? currentSettings.contextMenu,
            
            // Privacy
            anonymizeData: elements.anonymizeData?.checked ?? currentSettings.anonymizeData,
            encryptStorage: elements.encryptStorage?.checked ?? currentSettings.encryptStorage,
            clearOnClose: elements.clearOnClose?.checked ?? currentSettings.clearOnClose,
            dataRetention: parseInt(elements.dataRetention?.value) || currentSettings.dataRetention,
            
            // Advanced
            debugMode: elements.debugMode?.checked ?? currentSettings.debugMode,
            experimentalFeatures: elements.experimentalFeatures?.checked ?? currentSettings.experimentalFeatures,
            maxContentLength: parseInt(elements.maxContentLength?.value) || currentSettings.maxContentLength,
            customHeaders: elements.customHeaders?.value || currentSettings.customHeaders,
            
            // Statistics (manter valores existentes)
            totalRequests: currentSettings.totalRequests,
            successfulRequests: currentSettings.successfulRequests,
            totalResponseTime: currentSettings.totalResponseTime,
            lastUpdate: new Date().toISOString()
        };
        
        // Validar configurações
        if (!isValidUrl(newSettings.apiUrl)) {
            throw new Error('URL da API inválida');
        }
        
        if (newSettings.streamlitUrl && !isValidUrl(newSettings.streamlitUrl)) {
            throw new Error('URL do Streamlit inválida');
        }
        
        try {
            JSON.parse(newSettings.customHeaders);
        } catch {
            throw new Error('Headers customizados devem ser um JSON válido');
        }
        
        // Salvar no storage
        await chrome.storage.sync.set(newSettings);
        currentSettings = newSettings;
        
        // Aplicar tema
        applyTheme();
        
        // Atualizar contexto do menu se necessário
        await updateContextMenu();
        
        showStatus('✅ Todas as configurações foram salvas com sucesso!', 'success');
        if (elements.lastUpdate) {
            elements.lastUpdate.textContent = new Date().toLocaleString('pt-BR');
        }
        
        console.log('Configurações salvas:', newSettings);
    } catch (error) {
        console.error('Erro ao salvar configurações:', error);
        showStatus(`❌ Erro ao salvar: ${error.message}`, 'danger');
    }
}

// Verificar conexão com a API
async function checkConnection() {
    const startTime = Date.now();
    
    try {
        // Atualizar indicador para "verificando"
        if (elements.statusIndicator) {
            elements.statusIndicator.innerHTML = `
                <div class="spinner-border spinner-border-sm text-warning" role="status">
                    <span class="visually-hidden">Verificando...</span>
                </div>
            `;
        }
        if (elements.statusTitle) elements.statusTitle.textContent = 'Verificando conexão...';
        if (elements.statusDetails) elements.statusDetails.textContent = 'Aguarde...';
        
        const response = await fetch(`${currentSettings.apiUrl}/api/v1/extension/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...parseCustomHeaders()
            },
            signal: AbortSignal.timeout(currentSettings.timeout * 1000)
        });
        
        const responseTime = Date.now() - startTime;
        
        if (response.ok) {
            const data = await response.json();
            connectionStatus = {
                connected: true,
                lastCheck: new Date(),
                responseTime,
                version: data.version || 'N/A'
            };
            
            if (elements.statusIndicator) {
                elements.statusIndicator.innerHTML = '<i class="bi bi-check-circle-fill text-success fs-4"></i>';
            }
            if (elements.statusTitle) elements.statusTitle.textContent = 'Conectado com sucesso';
            if (elements.statusDetails) {
                elements.statusDetails.textContent = `Versão: ${data.version || 'N/A'} • Tempo: ${responseTime}ms`;
            }
            
            // Carregar endpoints disponíveis
            await loadEndpoints();
            
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
    } catch (error) {
        connectionStatus = {
            connected: false,
            lastCheck: new Date(),
            error: error.message
        };
        
        if (elements.statusIndicator) {
            elements.statusIndicator.innerHTML = '<i class="bi bi-x-circle-fill text-danger fs-4"></i>';
        }
        if (elements.statusTitle) elements.statusTitle.textContent = 'Falha na conexão';
        if (elements.statusDetails) elements.statusDetails.textContent = error.message;
        
        console.error('Erro na conexão:', error);
    }
}

// Carregar endpoints disponíveis
async function loadEndpoints() {
    try {
        const endpoints = [
            { path: '/api/v1/extension/health', method: 'GET', description: 'Health Check' },
            { path: '/api/v1/extension/scrape', method: 'POST', description: 'Scrape Página' },
            { path: '/api/v1/extension/analyze', method: 'POST', description: 'Analisar Conteúdo' },
            { path: '/agents', method: 'GET', description: 'Listar Agentes' },
            { path: '/health', method: 'GET', description: 'Status Sistema' }
        ];
        
        if (elements.endpointsList) {
            elements.endpointsList.innerHTML = endpoints.map(endpoint => `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                    <div>
                        <span class="badge bg-${endpoint.method === 'GET' ? 'success' : 'primary'} me-2">${endpoint.method}</span>
                        <small class="text-muted">${endpoint.path}</small>
                    </div>
                    <small>${endpoint.description}</small>
                </div>
            `).join('');
        }
        
    } catch (error) {
        if (elements.endpointsList) {
            elements.endpointsList.innerHTML = '<p class="text-danger">Erro ao carregar endpoints</p>';
        }
    }
}

// Carregar agentes disponíveis
async function loadAgents() {
    try {
        const response = await fetch(`${currentSettings.apiUrl}/agents`, {
            headers: { ...parseCustomHeaders() },
            signal: AbortSignal.timeout(currentSettings.timeout * 1000)
        });
        
        if (response.ok) {
            const data = await response.json();
            availableAgents = data.agents || [];
            
            // Atualizar select de agentes
            if (elements.defaultAgent) {
                elements.defaultAgent.innerHTML = `
                    <option value="">Selecione um agente...</option>
                    ${availableAgents.map(agent => `
                        <option value="${agent.id}" ${agent.id === currentSettings.defaultAgent ? 'selected' : ''}>
                            ${agent.name} (${agent.type})
                        </option>
                    `).join('')}
                `;
            }
            
            // Atualizar lista de agentes
            if (elements.agentsList) {
                elements.agentsList.innerHTML = availableAgents.map(agent => `
                    <div class="border rounded p-3 mb-2">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">${agent.name}</h6>
                                <span class="badge bg-secondary mb-2">${agent.type}</span>
                                <p class="mb-1 small text-muted">${agent.description || 'Sem descrição'}</p>
                                <small class="text-muted">Modelo: ${agent.model || 'N/A'}</small>
                            </div>
                            <button class="btn btn-outline-primary btn-sm" onclick="selectAgent('${agent.id}')">
                                Selecionar
                            </button>
                        </div>
                    </div>
                `).join('');
            }
            
        } else {
            throw new Error(`Erro ao carregar agentes: ${response.statusText}`);
        }
        
    } catch (error) {
        console.error('Erro ao carregar agentes:', error);
        if (elements.defaultAgent) {
            elements.defaultAgent.innerHTML = '<option value="">Erro ao carregar agentes</option>';
        }
        if (elements.agentsList) {
            elements.agentsList.innerHTML = '<p class="text-danger">Erro ao carregar agentes</p>';
        }
    }
}

// Selecionar agente
function selectAgent(agentId) {
    if (elements.defaultAgent) {
        elements.defaultAgent.value = agentId;
    }
    const agentName = availableAgents.find(a => a.id === agentId)?.name;
    if (agentName) {
        showStatus(`Agente selecionado: ${agentName}`, 'info');
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Botões principais
    if (elements.testConnection) elements.testConnection.addEventListener('click', checkConnection);
    if (elements.resetSettings) elements.resetSettings.addEventListener('click', resetSettings);
    if (elements.saveAll) elements.saveAll.addEventListener('click', saveAllSettings);
    if (elements.openDashboard) elements.openDashboard.addEventListener('click', openDashboard);
    
    // Botões avançados
    if (elements.viewLogs) elements.viewLogs.addEventListener('click', viewLogs);
    if (elements.exportSettings) elements.exportSettings.addEventListener('click', exportSettings);
    if (elements.importSettings) elements.importSettings.addEventListener('click', () => elements.importFile?.click());
    if (elements.importFile) elements.importFile.addEventListener('change', importSettings);
    
    // Auto-salvar em mudanças importantes
    if (elements.apiUrl) {
        elements.apiUrl.addEventListener('blur', () => {
            if (elements.apiUrl.value !== currentSettings.apiUrl) {
                checkConnection();
            }
        });
    }
    
    // Aplicar tema em tempo real
    elements.themeInputs.forEach(input => {
        input.addEventListener('change', applyTheme);
    });
    
    // Validação de campos
    if (elements.customHeaders) {
        elements.customHeaders.addEventListener('blur', validateCustomHeaders);
    }
}

// Resetar configurações
async function resetSettings() {
    if (confirm('⚠️ Tem certeza que deseja resetar todas as configurações? Esta ação não pode ser desfeita.')) {
        try {
            await chrome.storage.sync.clear();
            currentSettings = { ...DEFAULT_SETTINGS };
            await loadSettings();
            showStatus('🔄 Configurações resetadas para os valores padrão', 'warning');
        } catch (error) {
            showStatus('❌ Erro ao resetar configurações', 'danger');
        }
    }
}

// Abrir dashboard
function openDashboard() {
    chrome.tabs.create({ url: currentSettings.streamlitUrl });
}

// Ver logs
function viewLogs() {
    chrome.tabs.create({ url: 'chrome://extensions/?id=' + chrome.runtime.id });
}

// Exportar configurações
function exportSettings() {
    const dataStr = JSON.stringify(currentSettings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `rag-control-settings-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    showStatus('📥 Configurações exportadas com sucesso', 'success');
}

// Importar configurações
function importSettings(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = async (e) => {
        try {
            const imported = JSON.parse(e.target.result);
            
            // Validar estrutura
            if (typeof imported !== 'object') {
                throw new Error('Arquivo inválido');
            }
            
            // Mesclar com configurações padrão
            const newSettings = { ...DEFAULT_SETTINGS, ...imported };
            
            await chrome.storage.sync.set(newSettings);
            currentSettings = newSettings;
            await loadSettings();
            
            showStatus('📤 Configurações importadas com sucesso', 'success');
        } catch (error) {
            showStatus('❌ Erro ao importar configurações: ' + error.message, 'danger');
        }
    };
    reader.readAsText(file);
}

// Atualizar estatísticas
function updateStatistics() {
    if (elements.totalRequests) elements.totalRequests.textContent = currentSettings.totalRequests;
    
    const successRate = currentSettings.totalRequests > 0 
        ? Math.round((currentSettings.successfulRequests / currentSettings.totalRequests) * 100)
        : 0;
    if (elements.successRate) elements.successRate.textContent = successRate + '%';
    
    const avgTime = currentSettings.totalRequests > 0
        ? Math.round(currentSettings.totalResponseTime / currentSettings.totalRequests)
        : 0;
    if (elements.avgResponseTime) elements.avgResponseTime.textContent = avgTime + 'ms';
}

// Aplicar tema
function applyTheme() {
    const theme = document.querySelector('input[name="theme"]:checked')?.value || 'dark';
    document.documentElement.setAttribute('data-bs-theme', theme);
}

// Atualizar menu de contexto
async function updateContextMenu() {
    try {
        if (currentSettings.contextMenu) {
            chrome.contextMenus.create({
                id: 'rag-control-context',
                title: 'Enviar para RAG-Control',
                contexts: ['page', 'selection']
            });
        } else {
            chrome.contextMenus.removeAll();
        }
    } catch (error) {
        console.error('Erro ao atualizar menu de contexto:', error);
    }
}

// Funções utilitárias
function showStatus(message, type = 'info') {
    if (elements.statusMessage) {
        elements.statusMessage.textContent = message;
        elements.statusMessage.className = `alert alert-${type}`;
        elements.statusMessage.classList.remove('d-none');
        
        setTimeout(() => {
            elements.statusMessage.classList.add('d-none');
        }, 5000);
    }
}

function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch {
        return false;
    }
}

function parseCustomHeaders() {
    try {
        return JSON.parse(currentSettings.customHeaders);
    } catch {
        return {};
    }
}

function validateCustomHeaders() {
    if (!elements.customHeaders) return;
    
    try {
        JSON.parse(elements.customHeaders.value);
        elements.customHeaders.classList.remove('is-invalid');
        elements.customHeaders.classList.add('is-valid');
    } catch {
        elements.customHeaders.classList.remove('is-valid');
        elements.customHeaders.classList.add('is-invalid');
    }
}

// Expor funções globais
window.selectAgent = selectAgent; 