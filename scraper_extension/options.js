document.addEventListener('DOMContentLoaded', () => {
    const optionsForm = document.getElementById('options-form');
    const apiUrlInput = document.getElementById('api-url');
    const statusMessage = document.getElementById('status-message');

    const showStatus = (message, isError = false) => {
        statusMessage.textContent = message;
        statusMessage.className = `alert ${isError ? 'alert-danger' : 'alert-success'}`;
        statusMessage.classList.remove('d-none');
        setTimeout(() => {
            statusMessage.classList.add('d-none');
        }, 3000);
    };

    // Carrega as configurações salvas
    chrome.storage.sync.get(['apiUrl'], (result) => {
        if (result.apiUrl) {
            apiUrlInput.value = result.apiUrl;
        }
    });

    // Salva as novas configurações
    optionsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const apiUrl = apiUrlInput.value.trim();
        if (apiUrl) {
            chrome.storage.sync.set({ apiUrl }, () => {
                showStatus('Configurações salvas com sucesso!');
            });
        } else {
            showStatus('Por favor, insira uma URL válida.', true);
        }
    });
}); 