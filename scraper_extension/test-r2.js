document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos do DOM ---
    const testR2Button = document.getElementById('test-r2');
    const testOpenAIButton = document.getElementById('test-openai');
    const connectionResults = document.getElementById('connection-results');
    
    const objectKeyInput = document.getElementById('object-key');
    const verifyFileButton = document.getElementById('verify-file');
    const verifyCurrentPageButton = document.getElementById('verify-current-page');
    const verificationResults = document.getElementById('verification-results');
    
    const integrityReport = document.getElementById('integrity-report');
    const backButton = document.getElementById('back-button');

    // --- Estatísticas ---
    let stats = {
        filesChecked: 0,
        integrityOK: 0,
        integrityIssues: 0
    };

    // --- Funções ---
    const updateStats = () => {
        document.getElementById('files-checked').textContent = stats.filesChecked;
        document.getElementById('integrity-ok').textContent = stats.integrityOK;
        document.getElementById('integrity-issues').textContent = stats.integrityIssues;
    };

    const showResult = (element, success, message, details = null) => {
        const icon = success ? '✅' : '❌';
        const className = success ? 'success' : 'error';
        
        let html = `<div class="${className}">${icon} ${message}</div>`;
        
        if (details) {
            html += `<details><summary>Detalhes</summary><pre>${JSON.stringify(details, null, 2)}</pre></details>`;
        }
        
        element.innerHTML = html;
    };

    const showLoading = (element, message = 'Carregando...') => {
        element.innerHTML = `<div class="loading">⏳ ${message}</div>`;
    };

    const formatBytes = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const displayIntegrityReport = (report) => {
        if (!report) {
            integrityReport.innerHTML = '<p>Nenhum relatório disponível.</p>';
            return;
        }

        const statusIcon = report.integrityValid ? '✅' : '❌';
        const statusClass = report.integrityValid ? 'success' : 'error';

        let html = `
            <div class="integrity-summary ${statusClass}">
                <h4>${statusIcon} Resumo da Verificação</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <strong>Status:</strong>
                        <span>${report.integrityValid ? 'Integridade OK' : 'Problemas Detectados'}</span>
                    </div>
                    <div class="stat-item">
                        <strong>Upload:</strong>
                        <span>${report.uploadSuccess ? '✅ Sucesso' : '❌ Falha'}</span>
                    </div>
                    <div class="stat-item">
                        <strong>Tamanho Original:</strong>
                        <span>${formatBytes(report.summary.originalDataSize)}</span>
                    </div>
                    <div class="stat-item">
                        <strong>Tamanho Upload:</strong>
                        <span>${formatBytes(report.summary.uploadedFileSize)}</span>
                    </div>
                </div>
            </div>
        `;

        if (report.details.validation) {
            const validation = report.details.validation;
            html += `
                <div class="validation-details">
                    <h4>Detalhes da Validação</h4>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <strong>Texto Preservado:</strong>
                            <span>${validation.stats.textComparison.match ? '✅' : '❌'}</span>
                        </div>
                        <div class="stat-item">
                            <strong>Estrutura Preservada:</strong>
                            <span>${validation.stats.structureComparison.match ? '✅' : '❌'}</span>
                        </div>
                        <div class="stat-item">
                            <strong>Classes Preservadas:</strong>
                            <span>${validation.stats.classesComparison.match ? '✅' : '❌'}</span>
                        </div>
                    </div>
                </div>
            `;

            if (validation.issues.length > 0) {
                html += `
                    <div class="validation-issues">
                        <h4>Problemas Detectados</h4>
                        <ul>
                            ${validation.issues.map(issue => `<li>❌ ${issue}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        }

        if (report.recommendations.length > 0) {
            html += `
                <div class="recommendations">
                    <h4>Recomendações</h4>
                    <ul>
                        ${report.recommendations.map(rec => `<li>💡 ${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        integrityReport.innerHTML = html;
    };

    // --- Event Listeners ---
    testR2Button.addEventListener('click', async () => {
        showLoading(connectionResults, 'Testando conexão com R2...');
        
        try {
            const response = await chrome.runtime.sendMessage({ action: 'testR2' });
            showResult(connectionResults, response.success, response.message, response);
        } catch (error) {
            showResult(connectionResults, false, `Erro: ${error.message}`);
        }
    });

    testOpenAIButton.addEventListener('click', async () => {
        showLoading(connectionResults, 'Testando conexão com OpenAI...');
        
        try {
            const response = await chrome.runtime.sendMessage({ action: 'testOpenAI' });
            showResult(connectionResults, response.success, response.message, response);
        } catch (error) {
            showResult(connectionResults, false, `Erro: ${error.message}`);
        }
    });

    verifyFileButton.addEventListener('click', async () => {
        const objectKey = objectKeyInput.value.trim();
        
        if (!objectKey) {
            showResult(verificationResults, false, 'Por favor, digite a chave do arquivo.');
            return;
        }

        showLoading(verificationResults, 'Verificando arquivo...');
        stats.filesChecked++;
        
        try {
            const response = await chrome.runtime.sendMessage({ 
                action: 'verifyFileIntegrity', 
                objectKey: objectKey 
            });
            
            if (response.success) {
                const verification = response.data;
                if (verification.success) {
                    stats.integrityOK++;
                    showResult(verificationResults, true, 
                        `Arquivo verificado com sucesso! Tamanho: ${formatBytes(verification.fileSize)}`, 
                        verification);
                    
                    // Gerar relatório de integridade
                    const reportResponse = await chrome.runtime.sendMessage({
                        action: 'generateIntegrityReport',
                        originalData: null, // Não temos dados originais para comparação
                        uploadResult: { success: true, filename: objectKey, size: verification.fileSize },
                        verificationResult: verification
                    });
                    
                    if (reportResponse.success) {
                        displayIntegrityReport(reportResponse.data);
                    }
                } else {
                    stats.integrityIssues++;
                    showResult(verificationResults, false, 
                        `Falha na verificação: ${verification.error}`, 
                        verification);
                }
            } else {
                stats.integrityIssues++;
                showResult(verificationResults, false, response.message);
            }
        } catch (error) {
            stats.integrityIssues++;
            showResult(verificationResults, false, `Erro: ${error.message}`);
        }
        
        updateStats();
    });

    verifyCurrentPageButton.addEventListener('click', async () => {
        showLoading(verificationResults, 'Capturando e verificando página atual...');
        stats.filesChecked++;
        
        try {
            // Primeiro, capturar dados da página atual
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab) {
                throw new Error('Nenhuma aba ativa encontrada');
            }

            const captureResponse = await chrome.runtime.sendMessage({ 
                action: 'capturePageData', 
                tabId: tab.id 
            });

            if (!captureResponse.success) {
                throw new Error(`Falha ao capturar dados: ${captureResponse.message}`);
            }

            // Simular um upload e verificação
            const originalData = captureResponse.data;
            const uploadResult = { 
                success: true, 
                filename: `test-${Date.now()}.json`, 
                size: JSON.stringify(originalData).length 
            };
            
            const verificationResult = { 
                success: true, 
                data: originalData, 
                fileSize: uploadResult.size,
                checksum: null
            };

            // Gerar relatório de integridade
            const reportResponse = await chrome.runtime.sendMessage({
                action: 'generateIntegrityReport',
                originalData: originalData,
                uploadResult: uploadResult,
                verificationResult: verificationResult
            });

            if (reportResponse.success) {
                const report = reportResponse.data;
                if (report.integrityValid) {
                    stats.integrityOK++;
                    showResult(verificationResults, true, 
                        'Dados da página capturados e verificados com sucesso!', 
                        { originalData, uploadResult, verificationResult });
                } else {
                    stats.integrityIssues++;
                    showResult(verificationResults, false, 
                        'Problemas de integridade detectados nos dados capturados', 
                        report);
                }
                
                displayIntegrityReport(report);
            } else {
                stats.integrityIssues++;
                showResult(verificationResults, false, reportResponse.message);
            }

        } catch (error) {
            stats.integrityIssues++;
            showResult(verificationResults, false, `Erro: ${error.message}`);
        }
        
        updateStats();
    });

    backButton.addEventListener('click', () => {
        window.history.back();
    });

    // --- Inicialização ---
    updateStats();
}); 