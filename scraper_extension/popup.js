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
    };

    let apiUrl = '';
    let currentUrl = '';

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
        ui.saveButtonText.textContent = isSaving ? 'Salvando...' : 'Salvar';
        ui.saveSpinner.classList.toggle('d-none', !isSaving);
    };

    // Função Principal de Inicialização
    const initialize = async () => {
        showLoading();

        // 1. Obter a URL da API das configurações
        const settings = await chrome.storage.sync.get('apiUrl');
        apiUrl = settings.apiUrl;
        if (!apiUrl) {
            showError('URL da API não configurada. Por favor, acesse as opções da extensão.');
            return;
        }

        // 2. Obter a URL da aba ativa
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        currentUrl = tabs[0]?.url;
        if (!currentUrl || !currentUrl.startsWith('http')) {
            showError('A página atual não é uma URL válida para captura.');
            return;
        }

        // 3. Buscar a lista de agentes da API
        try {
            const response = await fetch(`${apiUrl}/api/v1/agents`);
            if (!response.ok) throw new Error(`Erro de rede: ${response.statusText}`);
            
            const agents = await response.json();
            if (agents.length === 0) {
                showError('Nenhum agente encontrado. Crie um agente no sistema primeiro.');
                return;
            }

            ui.agentSelect.innerHTML = agents.map(agent => `<option value="${agent.id}">${agent.name}</option>`).join('');
            showMain();
        } catch (error) {
            showError(`Falha ao carregar agentes: ${error.message}`);
        }
    };

    // Lógica para o botão Salvar
    const handleSave = async () => {
        const agentId = ui.agentSelect.value;
        if (!agentId) return;

        setSaving(true);
        
        try {
            const response = await fetch(`${apiUrl}/api/v1/capture_page`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: agentId, url: currentUrl })
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Ocorreu um erro desconhecido.');

            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon16.png',
                title: 'Sucesso!',
                message: result.message
            });
            window.close(); // Fecha o popup

        } catch (error) {
            setSaving(false);
            showError(`Falha ao salvar: ${error.message}`);
        }
    };

    // Adiciona o event listener e inicializa
    ui.saveButton.addEventListener('click', handleSave);
    initialize();
}); 