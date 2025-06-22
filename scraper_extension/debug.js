document.addEventListener('DOMContentLoaded', async () => {
    // --- Elementos do DOM ---
    const pageInfo = document.getElementById('page-info');
    const captureStats = document.getElementById('capture-stats');
    const elementsList = document.getElementById('elements-list');
    const classesList = document.getElementById('classes-list');
    const fullText = document.getElementById('full-text');
    const filterElements = document.getElementById('filter-elements');
    const copyTextButton = document.getElementById('copy-text');
    const downloadTextButton = document.getElementById('download-text');
    const downloadStructureButton = document.getElementById('download-structure');
    const showCleanedStructureButton = document.getElementById('show-cleaned-structure');
    const showCleanTextButton = document.getElementById('show-clean-text');
    const backButton = document.getElementById('back-button');
    const structureTree = document.getElementById('structure-tree');

    let pageData = null;
    let cleanedStructure = null;
    let cleanText = null;

    // --- Funções ---
    const formatBytes = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString('pt-BR');
    };

    const displayPageInfo = () => {
        if (!pageData) return;
        
        pageInfo.innerHTML = `
            <div class="info-grid">
                <div class="info-item">
                    <strong>URL:</strong>
                    <span>${pageData.url}</span>
                </div>
                <div class="info-item">
                    <strong>Título:</strong>
                    <span>${pageData.title}</span>
                </div>
                <div class="info-item">
                    <strong>Data/Hora:</strong>
                    <span>${formatDate(pageData.timestamp)}</span>
                </div>
            </div>
        `;
    };

    const displayCaptureStats = () => {
        if (!pageData) return;
        
        captureStats.innerHTML = `
            <div class="stats-grid">
                <div class="stat-item">
                    <strong>Texto (caracteres):</strong>
                    <span>${pageData.fullText.length.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <strong>Tamanho do texto:</strong>
                    <span>${formatBytes(new Blob([pageData.fullText]).size)}</span>
                </div>
                <div class="stat-item">
                    <strong>Classes CSS Únicas:</strong>
                    <span>${pageData.allClasses.length}</span>
                </div>
            </div>
        `;
    };

    const displayElements = (filter = '') => {
        if (!pageData) return;
        
        const filteredElements = pageData.elements.filter(element => 
            element.text.toLowerCase().includes(filter.toLowerCase()) ||
            element.tag.toLowerCase().includes(filter.toLowerCase()) ||
            element.className.toLowerCase().includes(filter.toLowerCase())
        );

        if (filteredElements.length === 0) {
            elementsList.innerHTML = '<p>Nenhum elemento encontrado com esse filtro.</p>';
            return;
        }

        elementsList.innerHTML = filteredElements.map(element => `
            <div class="element-item">
                <div class="element-header">
                    <span class="element-tag">${element.tag}</span>
                    <span class="element-class">${element.className || 'sem classe'}</span>
                    <span class="element-id">${element.id || 'sem id'}</span>
                </div>
                <div class="element-text">${element.text.substring(0, 200)}${element.text.length > 200 ? '...' : ''}</div>
            </div>
        `).join('');
    };

    const displayClasses = () => {
        if (!pageData) return;
        
        const classesArray = Array.from(pageData.classes).sort();
        
        if (classesArray.length === 0) {
            classesList.innerHTML = '<p>Nenhuma classe CSS encontrada.</p>';
            return;
        }

        classesList.innerHTML = `
            <div class="classes-grid">
                ${classesArray.map(className => `
                    <span class="class-tag">${className}</span>
                `).join('')}
            </div>
        `;
    };

    const renderStructure = (nodes, level = 0) => {
        let html = '<div class="structure-node">';
        for (const node of nodes) {
            const hasChildren = node.children && node.children.length > 0;
            const detailsId = `details-${node.tag}-${Math.random().toString(36).substr(2, 9)}`;

            html += `<div class="element-item" style="margin-left: ${level * 20}px;">`;
            html += `<details ${hasChildren ? '' : 'class="no-children"'}>`;
            html += `<summary class="element-header">
                        <span class="element-tag">&lt;${node.tag}&gt;</span>
                        ${node.classes.length > 0 ? `<span class="element-class">${node.classes.join(' ')}</span>` : ''}
                        ${node.id ? `<span class="element-id">#${node.id}</span>` : ''}
                    </summary>`;
            
            if (node.text) {
                html += `<div class="element-text">${node.text}</div>`;
            }

            if (hasChildren) {
                html += renderStructure(node.children, level + 1);
            }
            
            html += `</details></div>`;
        }
        html += '</div>';
        return html;
    };

    const displayStructure = (structure = null) => {
        const structureToShow = structure || (pageData ? pageData.structure : null);
        if (!structureToShow) return;
        structureTree.innerHTML = renderStructure(structureToShow);
    };

    const displayFullText = () => {
        if (!pageData) return;
        fullText.innerHTML = `<div class="text-content"><pre>${pageData.fullText}</pre></div>`;
    };

    // --- Event Listeners ---
    filterElements.addEventListener('input', (e) => {
        displayElements(e.target.value);
    });

    copyTextButton.addEventListener('click', async () => {
        if (!pageData) return;
        
        try {
            await navigator.clipboard.writeText(pageData.textContent);
            copyTextButton.textContent = 'Copiado!';
            setTimeout(() => {
                copyTextButton.textContent = 'Copiar Texto';
            }, 2000);
        } catch (error) {
            console.error('Erro ao copiar texto:', error);
        }
    });

    downloadTextButton.addEventListener('click', () => {
        if (!pageData) return;
        
        const blob = new Blob([pageData.textContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pagina_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    downloadStructureButton.addEventListener('click', () => {
        if (!pageData) return;
        const filename = `structure-${pageData.title.replace(/[\\?%*:|"<>]/g, '') || 'pagina'}.json`;
        const blob = new Blob([JSON.stringify(pageData, null, 2)], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    showCleanedStructureButton.addEventListener('click', () => {
        if (!cleanedStructure) {
            // Aplicar limpeza se ainda não foi feita
            cleanedStructure = cleanDOMStructure(pageData.structure, {
                removeEmptyElements: true,
                removeCSSClasses: true,
                removeProgressLoaders: true,
                removeA11yElements: true,
                removePrintElements: true,
                preserveTextElements: true,
                maxDepth: 10
            });
        }
        displayStructure(cleanedStructure);
    });

    showCleanTextButton.addEventListener('click', () => {
        if (!cleanText) {
            // Extrair texto limpo se ainda não foi feito
            if (!cleanedStructure) {
                cleanedStructure = cleanDOMStructure(pageData.structure, {
                    removeEmptyElements: true,
                    removeCSSClasses: true,
                    removeProgressLoaders: true,
                    removeA11yElements: true,
                    removePrintElements: true,
                    preserveTextElements: true,
                    maxDepth: 10
                });
            }
            cleanText = extractCleanText(cleanedStructure);
        }
        fullText.innerHTML = `<div class="text-content"><pre>${cleanText}</pre></div>`;
    });

    backButton.addEventListener('click', () => {
        window.history.back();
    });

    // --- Inicialização ---
    try {
        // Obter a aba ativa
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab) {
            throw new Error('Nenhuma aba ativa encontrada');
        }

        // Capturar dados da página
        const response = await chrome.runtime.sendMessage({ 
            action: 'capturePageData', 
            tabId: tab.id 
        });

        if (response.success) {
            pageData = response.data;
            displayPageInfo();
            displayCaptureStats();
            displayElements();
            displayClasses();
            displayStructure();
            displayFullText();
        } else {
            throw new Error(response.message);
        }

    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        pageInfo.innerHTML = `<p class="error">Erro ao carregar dados: ${error.message}</p>`;
        captureStats.innerHTML = '<p class="error">Erro ao carregar estatísticas</p>';
        elementsList.innerHTML = '<p class="error">Erro ao carregar elementos</p>';
        classesList.innerHTML = '<p class="error">Erro ao carregar classes</p>';
        fullText.innerHTML = '<p class="error">Erro ao carregar texto</p>';
    }

    // Funções auxiliares para limpeza (copiadas do background.js)
    function cleanDOMStructure(structure, options = {}) {
        const {
            removeEmptyElements = true,
            removeCSSClasses = true,
            removeProgressLoaders = true,
            removeA11yElements = true,
            removePrintElements = true,
            preserveTextElements = true,
            maxDepth = 10
        } = options;

        function shouldRemoveElement(element, depth = 0) {
            if (depth > maxDepth) return false;

            const alwaysRemove = [
                'script', 'style', 'noscript', 'meta', 'link', 'svg', 'path',
                'iframe', 'embed', 'object', 'applet', 'canvas', 'video', 'audio'
            ];
            
            if (alwaysRemove.includes(element.tag)) return true;

            if (removeProgressLoaders && element.classes.some(cls => 
                cls.includes('progress') || cls.includes('loader') || cls.includes('loading'))) {
                return true;
            }

            if (removeA11yElements && element.classes.some(cls => 
                cls.includes('a11y') || cls.includes('skip') || cls.includes('sr-only'))) {
                return true;
            }

            if (removePrintElements && element.classes.some(cls => 
                cls.includes('print') || cls.includes('unprintable'))) {
                return true;
            }

            if (removeEmptyElements && !element.text && element.children.length === 0) {
                return true;
            }

            return false;
        }

        function hasTextContent(element, depth = 0) {
            if (depth > maxDepth) return false;
            
            if (element.text && element.text.trim()) return true;
            
            return element.children.some(child => hasTextContent(child, depth + 1));
        }

        function cleanElement(element, depth = 0) {
            if (shouldRemoveElement(element, depth)) {
                return null;
            }

            const cleanedElement = {
                tag: element.tag,
                id: element.id,
                text: element.text,
                children: []
            };

            if (!removeCSSClasses) {
                cleanedElement.classes = element.classes;
            } else {
                const essentialClasses = element.classes.filter(cls => {
                    return cls.includes('content') || 
                           cls.includes('text') || 
                           cls.includes('title') || 
                           cls.includes('heading') ||
                           cls.includes('article') ||
                           cls.includes('section') ||
                           cls.includes('main') ||
                           cls.includes('body');
                });
                
                if (essentialClasses.length > 0) {
                    cleanedElement.classes = essentialClasses;
                }
            }

            for (const child of element.children) {
                const cleanedChild = cleanElement(child, depth + 1);
                if (cleanedChild !== null) {
                    cleanedElement.children.push(cleanedChild);
                }
            }

            if (!cleanedElement.text && cleanedElement.children.length > 0) {
                return cleanedElement;
            }

            if (cleanedElement.text && cleanedElement.text.trim()) {
                return cleanedElement;
            }

            if (cleanedElement.children.some(child => hasTextContent(child))) {
                return cleanedElement;
            }

            if (removeEmptyElements && !cleanedElement.text && cleanedElement.children.length === 0) {
                return null;
            }

            return cleanedElement;
        }

        const cleanedStructure = [];
        for (const element of structure) {
            const cleanedElement = cleanElement(element);
            if (cleanedElement !== null) {
                cleanedStructure.push(cleanedElement);
            }
        }

        return cleanedStructure;
    }

    function extractCleanText(structure) {
        let cleanText = '';
        
        function extractFromElement(element) {
            if (element.text && element.text.trim()) {
                cleanText += element.text.trim() + '\n';
            }
            
            for (const child of element.children) {
                extractFromElement(child);
            }
        }
        
        for (const element of structure) {
            extractFromElement(element);
        }
        
        return cleanText.trim();
    }
}); 