document.addEventListener('DOMContentLoaded', () => {
    const r2Status = document.getElementById('r2-status');
    const openaiStatus = document.getElementById('openai-status');
    const testR2Button = document.getElementById('test-r2-button');
    const testOpenAIButton = document.getElementById('test-openai-button');
    const newTagInput = document.getElementById('new-tag-input');
    const addTagButton = document.getElementById('add-tag-button');
    const tagsList = document.getElementById('tags-list');
    const openaiEnabled = document.getElementById('openai-enabled');
    const cleanStructureEnabled = document.getElementById('clean-structure-enabled');
    const removeCSSClasses = document.getElementById('remove-css-classes');
    const removeProgressLoaders = document.getElementById('remove-progress-loaders');

    const updateStatus = (element, result) => {
        if (!element) return;

        if (result && result.success) {
            element.textContent = 'Sucesso';
            element.className = 'status-badge status-success';
        } else {
            element.textContent = 'Falhou';
            element.className = 'status-badge status-error';
            console.error("Detalhes do erro:", result ? result.message : 'Resposta indefinida ou erro de comunicação.');
        }
    };

    const testR2 = () => {
        if (!r2Status) return;
        r2Status.textContent = 'Testando...';
        r2Status.className = 'status-badge status-testing';
        chrome.runtime.sendMessage({ action: 'testR2' }, (response) => {
            if (chrome.runtime.lastError) {
                updateStatus(r2Status, { success: false, message: chrome.runtime.lastError.message });
                return;
            }
            updateStatus(r2Status, response);
        });
    };

    const testOpenAI = () => {
        if (!openaiStatus) return;
        openaiStatus.textContent = 'Testando...';
        openaiStatus.className = 'status-badge status-testing';
        chrome.runtime.sendMessage({ action: 'testOpenAI' }, (response) => {
            if (chrome.runtime.lastError) {
                updateStatus(openaiStatus, { success: false, message: chrome.runtime.lastError.message });
                return;
            }
            updateStatus(openaiStatus, response);
        });
    };

    const renderTags = (tags = []) => {
        tagsList.innerHTML = '';
        if (tags.length === 0) {
            tagsList.innerHTML = '<li>Nenhuma tag cadastrada.</li>';
            return;
        }
        tags.forEach(tag => {
            const li = document.createElement('li');
            li.textContent = tag;
            const removeBtn = document.createElement('button');
            removeBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
            removeBtn.className = 'danger-text';
            removeBtn.onclick = () => removeTag(tag);
            li.appendChild(removeBtn);
            tagsList.appendChild(li);
        });
    };

    const loadTags = async () => {
        const { tags = [] } = await chrome.storage.sync.get('tags');
        renderTags(tags.sort());
    };

    const addTag = async () => {
        const tag = newTagInput.value.trim();
        if (!tag) return;
        const { tags = [] } = await chrome.storage.sync.get('tags');
        if (!tags.includes(tag)) {
            const newTags = [...tags, tag];
            await chrome.storage.sync.set({ tags: newTags });
            newTagInput.value = '';
            loadTags();
        }
    };

    const removeTag = async (tagToRemove) => {
        if (!confirm(`Tem certeza que deseja remover a tag "${tagToRemove}"?`)) return;
        const { tags = [] } = await chrome.storage.sync.get('tags');
        const newTags = tags.filter(t => t !== tagToRemove);
        await chrome.storage.sync.set({ tags: newTags });
        loadTags();
    };

    const loadOpenAISettings = async () => {
        const { openaiEnabled: enabled = true } = await chrome.storage.sync.get('openaiEnabled');
        if (openaiEnabled) {
            openaiEnabled.checked = enabled;
        }
    };

    const saveOpenAISettings = async () => {
        if (openaiEnabled) {
            await chrome.storage.sync.set({ openaiEnabled: openaiEnabled.checked });
        }
    };

    const loadStructureSettings = async () => {
        const { 
            cleanStructureEnabled: cleanEnabled = true,
            removeCSSClasses: removeClasses = true,
            removeProgressLoaders: removeLoaders = true
        } = await chrome.storage.sync.get(['cleanStructureEnabled', 'removeCSSClasses', 'removeProgressLoaders']);
        
        if (cleanStructureEnabled) cleanStructureEnabled.checked = cleanEnabled;
        if (removeCSSClasses) removeCSSClasses.checked = removeClasses;
        if (removeProgressLoaders) removeProgressLoaders.checked = removeLoaders;
    };

    const saveStructureSettings = async () => {
        const settings = {};
        if (cleanStructureEnabled) settings.cleanStructureEnabled = cleanStructureEnabled.checked;
        if (removeCSSClasses) settings.removeCSSClasses = removeCSSClasses.checked;
        if (removeProgressLoaders) settings.removeProgressLoaders = removeProgressLoaders.checked;
        
        await chrome.storage.sync.set(settings);
    };

    if (testR2Button) {
        testR2Button.addEventListener('click', testR2);
    }
    if (testOpenAIButton) {
        testOpenAIButton.addEventListener('click', testOpenAI);
    }
    addTagButton.addEventListener('click', addTag);
    newTagInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') addTag(); });
    openaiEnabled.addEventListener('change', saveOpenAISettings);
    cleanStructureEnabled.addEventListener('change', saveStructureSettings);
    removeCSSClasses.addEventListener('change', saveStructureSettings);
    removeProgressLoaders.addEventListener('change', saveStructureSettings);

    testR2();
    testOpenAI();
    loadTags();
    loadOpenAISettings();
    loadStructureSettings();
});
