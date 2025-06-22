document.addEventListener('DOMContentLoaded', () => {
    // Mapeamento de elementos da UI
    const ui = {
        loadingState: document.getElementById('loading-state'),
        errorState: document.getElementById('error-state'),
        mainState: document.getElementById('main-state'),
        agentSelect: document.getElementById('agent-select'),
        saveButton: document.getElementById('save-button'),
        saveButtonText: document.getElementById('save-button-text'),
        saveSpinner: document.getElementById('save-spinner'),
        pageInfo: document.getElementById('page-info'),
        agentCount: document.getElementById('agent-count')
    };

    let apiUrl = '';
    let currentUrl = '';
    let currentTitle = '';

    // Funções de controle de estado da UI
    const showLoading = () => {
        ui.loadingState.classList.remove('d-none');
        ui.errorState.classList.add('d-none');
        ui.mainState.classList.add('d-none');
    };

    const showError = (message) => {
        ui.errorState.textContent = message;
        ui.loadingState.classList.add('d-none');
        ui.errorState.classList.remove('d-none');
        ui.mainState.classList.add('d-none');
    };

    const showMain = () => {
        ui.loadingState.classList.add('d-none');
        ui.errorState.classList.add('d-none');
        ui.mainState.classList.remove('d-none');
    };
    
    const setSaving = (isSaving) => {
        ui.saveButton.disabled = isSaving;
        ui.saveButtonText.textContent = isSaving ? 'Capturando...' : 'Capturar Página';
        ui.saveSpinner.classList.toggle('d-none', !isSaving);
    };

    // Função para validar configurações
    const validateSettings = async () => {
        const settings = await chrome.storage.sync.get(['apiUrl']);
        apiUrl = settings.apiUrl;
        
        console.log('API URL configurada:', apiUrl); // Debug
        
        if (!apiUrl) {
            throw new Error('URL da API não configurada. Acesse as opções da extensão e configure: http://192.168.8.4:5000');
        }
        
        // Testar conectividade com a nova API isolada
        try {
            console.log('Testando conectividade com:', `${apiUrl}/api/v1/extension/health`); // Debug
            
            const response = await fetch(`${apiUrl}/api/v1/extension/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                mode: 'cors'
            });
            
            console.log('Response status:', response.status); // Debug
            
            if (!response.ok) throw new Error(`API não disponível: ${response.status} ${response.statusText}`);
            
            const health = await response.json();
            console.log('Health response:', health); // Debug
            
            if (!health.success) throw new Error('API da extensão não está funcionando');
            
        } catch (error) {
            console.error('Erro de conectividade:', error); // Debug
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error(`Não foi possível conectar ao servidor. Verifique se o servidor está rodando em ${apiUrl}`);
            }
            throw new Error(`Falha na conectividade: ${error.message}`);
        }
    };

    // Função para obter informações da aba atual
    const getCurrentPageInfo = async () => {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        const tab = tabs[0];
        
        if (!tab?.url || !tab.url.startsWith('http')) {
            throw new Error('A página atual não é uma URL válida para captura.');
        }
        
        currentUrl = tab.url;
        currentTitle = tab.title || 'Página sem título';
        
        // Atualizar UI com informações da página
        if (ui.pageInfo) {
            ui.pageInfo.innerHTML = `
                <strong>Página:</strong> ${currentTitle}<br>
                <small class="text-muted">${currentUrl}</small>
            `;
        }
    };

    // Função para carregar agentes da nova API
    const loadAgents = async () => {
        try {
            const response = await fetch(`${apiUrl}/api/v1/extension/agents`);
            if (!response.ok) throw new Error(`Erro de rede: ${response.statusText}`);
            
            const result = await response.json();
            if (!result.success) throw new Error(result.error || 'Erro desconhecido');
            
            const agents = result.agents;
            if (agents.length === 0) {
                throw new Error('Nenhum agente ativo encontrado. Crie um agente no sistema primeiro.');
            }

            // Preencher select de agentes
            ui.agentSelect.innerHTML = agents.map(agent => 
                `<option value="${agent.id}" title="${agent.description || ''}">${agent.name}</option>`
            ).join('');
            
            // Atualizar contador de agentes
            if (ui.agentCount) {
                ui.agentCount.textContent = `${agents.length} agente(s) disponível(is)`;
            }
            
            return agents;
            
        } catch (error) {
            throw new Error(`Falha ao carregar agentes: ${error.message}`);
        }
    };

    // Função Principal de Inicialização
    const initialize = async () => {
        showLoading();

        try {
            // 1. Validar configurações e conectividade
            await validateSettings();
            
            // 2. Obter informações da página atual
            await getCurrentPageInfo();

            // 3. Carregar lista de agentes
            await loadAgents();
            
            showMain();
            
        } catch (error) {
            showError(error.message);
        }
    };

    // Lógica para o botão Capturar
    const handleCapture = async () => {
        const agentId = ui.agentSelect.value;
        if (!agentId) {
            showError('Por favor, selecione um agente.');
            return;
        }

        setSaving(true);
        
        try {
            console.log('Iniciando captura para agente:', agentId); // Debug
            console.log('URL a capturar:', currentUrl); // Debug
            
            // Usar a nova API isolada para captura
            const response = await fetch(`${apiUrl}/api/v1/extension/capture_page`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    agent_id: agentId, 
                    url: currentUrl 
                })
            });

            console.log('Capture response status:', response.status); // Debug
            
            let result;
            try {
                result = await response.json();
                console.log('Capture response:', result); // Debug
            } catch (jsonError) {
                console.error('Erro ao parsear JSON:', jsonError); // Debug
                throw new Error('Resposta inválida do servidor');
            }
            
            if (!response.ok || !result.success) {
                throw new Error(result.error || `Erro HTTP ${response.status}: ${response.statusText}`);
            }

            // Notificação de sucesso
            try {
                chrome.notifications.create({
                    type: 'basic',
                    title: '🎉 Captura Realizada!',
                    message: `Página adicionada ao agente "${result.agent_name}"`
                });
            } catch (error) {
                console.log('Notificação não pôde ser criada:', error);
            }
            
            // Fechar popup após sucesso
            setTimeout(() => window.close(), 1000);

        } catch (error) {
            console.error('Erro na captura:', error); // Debug
            setSaving(false);
            
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                showError(`Não foi possível conectar ao servidor. Verifique se está rodando em ${apiUrl}`);
            } else {
                showError(`Falha na captura: ${error.message}`);
            }
        }
    };

    // Event Listeners
    ui.saveButton.addEventListener('click', handleCapture);
    
    // Inicializar a extensão
    initialize();
}); 