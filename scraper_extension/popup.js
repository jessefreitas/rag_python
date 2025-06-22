document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos do DOM ---
    const tagSelect = document.getElementById('tag-select');
    const saveButton = document.getElementById('save-button');
    const optionsButton = document.getElementById('options-button');
    const statusDiv = document.getElementById('status');

    // --- Funções ---
    const showStatus = (message, isError = false) => {
        statusDiv.textContent = message;
        statusDiv.className = isError ? 'status-error' : 'status-success';
        statusDiv.style.display = 'block';
    };

    const loadTags = async () => {
        const { tags = [] } = await chrome.storage.sync.get('tags');
        tags.sort().forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = tag;
            tagSelect.appendChild(option);
        });
    };

    // --- Event Listeners ---
    saveButton.addEventListener('click', () => {
        showStatus('Corrigindo e salvando...', false);
        saveButton.disabled = true;
        const tag = tagSelect.value || null;

        chrome.runtime.sendMessage({ action: 'savePage', data: { tag } }, (response) => {
            if (chrome.runtime.lastError) {
                showStatus(`Erro: ${chrome.runtime.lastError.message}`, true);
                saveButton.disabled = false;
                return;
            }
            if (response.success) {
                showStatus(response.message, false);
                setTimeout(() => window.close(), 2000);
            } else {
                showStatus(response.message, true);
                saveButton.disabled = false;
            }
        });
    });

    optionsButton.addEventListener('click', () => {
        chrome.runtime.openOptionsPage();
    });
    
    // --- Carga Inicial ---
    loadTags();
});
