document.addEventListener('DOMContentLoaded', () => {
    const versionDetails = document.getElementById('version-details');
    const logsContainer = document.getElementById('logs-container');
    const searchFilterInput = document.getElementById('search-filter');
    const levelFilterSelect = document.getElementById('level-filter');
    const refreshButton = document.getElementById('refresh-button');
    const exportButton = document.getElementById('export-button');
    const clearButton = document.getElementById('clear-button');

    let allLogs = [];

    const displayVersionInfo = (info) => {
        if (!info || !info.version || !info.history) {
            versionDetails.innerHTML = "<p>Não foi possível carregar as informações da versão.</p>";
            return;
        }
        let html = `<p><strong>Versão Atual:</strong> <span class="version-number">${info.version}</span></p>
                    <ul class="version-list">`;
        
        info.history.forEach(v => {
             html += `<li><span class="version-number">v${v.version}</span> (${v.date}): ${v.changes.join(', ')}</li>`;
        });
        
        html += '</ul>';
        versionDetails.innerHTML = html;
    };

    const displayLogs = (logs) => {
        if (!logs || logs.length === 0) {
            logsContainer.innerHTML = '<div class="no-logs">Nenhum log encontrado.</div>';
            return;
        }
        logsContainer.innerHTML = logs.map(log => `
            <div class="log-entry log-${log.level.toLowerCase()}">
                <div class="log-header">
                    <span class="log-level">[${log.level}]</span>
                    <span class="log-timestamp">${new Date(log.timestamp).toLocaleString('pt-BR')}</span>
                </div>
                <div class="log-message">${log.message}</div>
                ${log.data ? `<pre class="log-data">${log.data}</pre>` : ''}
            </div>
        `).join('');
    };

    const filterLogs = () => {
        const levelFilter = levelFilterSelect ? levelFilterSelect.value : '';
        const searchFilter = searchFilterInput ? searchFilterInput.value.toLowerCase() : '';
        let filtered = allLogs;

        if (levelFilter) {
            filtered = filtered.filter(log => log.level === levelFilter);
        }
        if (searchFilter) {
            filtered = filtered.filter(log => 
                log.message.toLowerCase().includes(searchFilter) ||
                (log.data && log.data.toLowerCase().includes(searchFilter))
            );
        }
        displayLogs(filtered);
    };

    const refreshAll = () => {
        chrome.runtime.sendMessage({ action: 'getVersionInfo' }, (response) => {
            if (chrome.runtime.lastError) {
                versionDetails.innerHTML = `<p>Erro ao carregar versão: ${chrome.runtime.lastError.message}</p>`;
            } else {
                displayVersionInfo(response);
            }
        });

        chrome.runtime.sendMessage({ action: 'getLogs' }, (response) => {
             if (chrome.runtime.lastError) {
                logsContainer.innerHTML = `<div class="no-logs">Erro ao carregar logs: ${chrome.runtime.lastError.message}</div>`;
            } else {
                allLogs = response || [];
                filterLogs();
            }
        });
    };

    const clearLogs = () => {
        if (confirm('Tem certeza que deseja limpar todos os logs? Esta ação não pode ser desfeita.')) {
            chrome.runtime.sendMessage({ action: 'clearLogs' }, () => {
                refreshAll();
            });
        }
    };

    const exportLogs = () => {
        if (allLogs.length === 0) {
            alert("Não há logs para exportar.");
            return;
        }
        const dataStr = JSON.stringify(allLogs, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `legallinda-logs-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };
    
    if(refreshButton) refreshButton.addEventListener('click', refreshAll);
    if(clearButton) clearButton.addEventListener('click', clearLogs);
    if(exportButton) exportButton.addEventListener('click', exportLogs);
    if(levelFilterSelect) levelFilterSelect.addEventListener('change', filterLogs);
    if(searchFilterInput) searchFilterInput.addEventListener('keyup', filterLogs);

    refreshAll();
}); 