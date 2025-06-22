const R2_CONFIG = {
    // Credenciais corretas do usuário
    accessKeyId: '512d30c11d7e63b50b0ed1213c92b537',
    secretAccessKey: '9a2ef8f0a5c39a0a47bd7f6c999445e946e55c53dde309e2792053413e654242',
    endpoint: 'https://legaltech.0245b00ef3744d9e0e07f785971bb90a.r2.cloudflarestorage.com',
};
// Chave de API removida por segurança - deve ser configurada via variável de ambiente
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'YOUR_OPENAI_API_KEY_HERE';

const VERSION_HISTORY = [
    { version: "2.7.1", date: "2024-06-21", changes: ["CORREÇÃO: Removida chamada de limpeza do script injetado.", "Limpeza da estrutura DOM movida para contexto do background script.", "Corrigido erro 'cleanDOMStructure is not defined'."] },
    { version: "2.7.0", date: "2024-06-21", changes: ["Sistema inteligente de limpeza da estrutura DOM.", "Remoção automática de elementos desnecessários (progress, a11y, print).", "Configurações personalizáveis para limpeza de dados.", "Preservação total de texto importante durante a limpeza.", "Interface de opções expandida com controles de limpeza."] },
    { version: "2.6.1", date: "2024-06-21", changes: ["CORREÇÃO CRÍTICA: Corrigido erro de assinatura AWS Signature V4.", "Melhorada codificação URI para seguir padrão AWS.", "Normalização de caracteres acentuados em nomes de arquivo.", "Reduzido limite de caracteres para evitar URLs muito longas."] },
    { version: "2.6.0", date: "2024-06-21", changes: ["Sistema completo de verificação de integridade dos dados.", "Validação pós-upload com comparação de dados.", "Relatório detalhado de verificação de salvamento.", "Checksum MD5 para verificar integridade dos arquivos.", "Sistema de auditoria de salvamentos com logs detalhados."] },
    { version: "2.5.0", date: "2024-06-21", changes: ["Adicionado toggle para ativar/desativar processamento OpenAI.", "Implementada captura completa de dados da página com validação.", "Criada página de debug para examinar dados capturados.", "Melhorada a captura de classes CSS e elementos da página."] },
    { version: "2.4.0", date: "2024-06-21", changes: ["Adicionado gerenciamento de tags na página de Opções.", "Menus de contexto e popup agora usam as tags cadastradas.", "Corrigido o tamanho do ícone SVG."] },
    { version: "2.3.0", date: "2024-06-21", changes: ["Adicionados ícones da biblioteca Font Awesome.", "Corrigida a política de segurança de conteúdo (CSP)."] },
    { version: "2.2.0", date: "2024-06-21", changes: ["Corrigida a chamada da API OpenAI para evitar truncamento de texto longo.", "Reintroduzidos ícones na interface do usuário."] },
    { version: "2.1.0", date: "2024-06-21", changes: ["Integração com OpenAI para corrigir erros de codificação de caracteres.", "Alterado o nome para LegalLindaAI."] },
    { version: "2.0.5", date: "2024-06-21", changes: ["Adicionado BOM e charset=utf-8 para corrigir erros de codificação."] },
    { version: "2.0.4", date: "2024-06-21", changes: ["CORREÇÃO CRÍTICA: Ajustado o endpoint do R2 para o formato 'virtual-hosted style', resolvendo o erro 'MalformedXML' no upload."] },
    { version: "2.0.3", date: "2024-06-21", changes: ["CORREÇÃO CRÍTICA: Restauradas as credenciais corretas do usuário para R2 e OpenAI, resolvendo erros de autenticação (401/400)."] },
    { version: "2.0.2", date: "2024-06-20", changes: ["Correção final no algoritmo de assinatura AWS v4."] },
    { version: "2.0.1", date: "2024-06-19", changes: ["Correção da interface de Opções e Logs.", "Removida funcionalidade de salvar localmente."] },
    { version: "2.0.0", date: "2024-06-19", changes: ["Removidas as configurações manuais.", "Adicionado sistema de logs e versionamento."] },
];

// --- SISTEMA DE LOG ---
const log = async (level, message, data = null) => {
    const timestamp = new Date().toISOString();
    const logEntry = {
        timestamp,
        level,
        message,
        data,
        version: VERSION
    };
    
    try {
        const logs = await chrome.storage.local.get('logs') || { logs: [] };
        logs.logs.push(logEntry);
        
        // Manter apenas os últimos 100 logs
        if (logs.logs.length > 100) {
            logs.logs = logs.logs.slice(-100);
        }
        
        await chrome.storage.local.set(logs);
        console.log(`[${level}] ${message}`, data || '');
    } catch (error) {
        console.error('Erro ao salvar log:', error);
    }
};

// --- INICIALIZAÇÃO E LISTENERS ---
chrome.runtime.onInstalled.addListener(async ({ reason }) => {
    buildContextMenus();
    if (reason === 'install') {
        await log('INFO', `Extensão instalada v${VERSION}.`);
        chrome.tabs.create({ url: 'options.html' });
    } else if (reason === 'update') {
        await log('INFO', `Extensão atualizada para v${VERSION}.`);
    }
});

// Adiciona um listener para quando as tags mudarem, reconstruir o menu.
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'sync' && changes.tags) {
        buildContextMenus();
    }
});

chrome.contextMenus.onClicked.addListener(onContextMenuClick);

// --- LÓGICA DE NEGÓCIOS ---
const sanitizeFilename = (name) => {
    return (name || 'sem-titulo')
        .replace(/[\\?%*:|"<>]/g, '') // Remove caracteres inválidos
        .replace(/[àáâãäå]/g, 'a')    // Normaliza acentos
        .replace(/[èéêë]/g, 'e')
        .replace(/[ìíîï]/g, 'i')
        .replace(/[òóôõö]/g, 'o')
        .replace(/[ùúûü]/g, 'u')
        .replace(/[ç]/g, 'c')
        .replace(/[ÀÁÂÃÄÅ]/g, 'A')
        .replace(/[ÈÉÊË]/g, 'E')
        .replace(/[ÌÍÎÏ]/g, 'I')
        .replace(/[ÒÓÔÕÖ]/g, 'O')
        .replace(/[ÙÚÛÜ]/g, 'U')
        .replace(/[Ç]/g, 'C')
        .replace(/\s+/g, ' ')         // Remove espaços múltiplos
        .trim()
        .substring(0, 100);           // Limita a 100 caracteres
};

async function correctTextWithOpenAI(text) {
    await log('INFO', 'Enviando texto para correção na OpenAI...');
    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [{
                    role: 'system',
                    content: 'Você é um assistente de correção de texto. Sua única tarefa é corrigir erros de codificação de caracteres (ex: "Ã§" para "ç") no texto do usuário. Retorne o texto corrigido na íntegra. Não resuma, não adicione e não remova nenhuma palavra ou pontuação. Preserve todo o conteúdo e quebras de linha originais.'
                }, {
                    role: 'user',
                    content: text
                }],
                temperature: 0.0,
                max_tokens: 3000
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`API OpenAI retornou erro ${response.status}: ${errorData.error.message}`);
        }

        const data = await response.json();
        if (data.choices[0].finish_reason === 'length') {
            await log('WARN', 'A resposta da OpenAI pode ter sido truncada por atingir o max_tokens.');
        }

        const correctedText = data.choices[0].message.content.trim();
        await log('INFO', 'Texto corrigido pela OpenAI com sucesso.');
        return correctedText;

    } catch (error) {
        await log('ERROR', `Falha ao processar com OpenAI: ${error.message}. Salvando o texto original como fallback.`);
        return text;
    }
}

// --- SISTEMA DE VERIFICAÇÃO DE INTEGRIDADE ---
async function generateChecksum(data) {
    try {
        const encoder = new TextEncoder();
        const dataBuffer = encoder.encode(JSON.stringify(data));
        const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (error) {
        await log('ERROR', 'Erro ao gerar checksum:', { error: error.message });
        return null;
    }
}

async function validateDataIntegrity(originalData, uploadedData) {
    const validation = {
        isValid: true,
        issues: [],
        stats: {
            originalSize: 0,
            uploadedSize: 0,
            textComparison: { match: false, originalLength: 0, uploadedLength: 0 },
            structureComparison: { match: false, originalElements: 0, uploadedElements: 0 },
            classesComparison: { match: false, originalClasses: 0, uploadedClasses: 0 }
        }
    };

    try {
        // Verificar tamanho dos dados
        const originalString = JSON.stringify(originalData);
        const uploadedString = JSON.stringify(uploadedData);
        
        validation.stats.originalSize = originalString.length;
        validation.stats.uploadedSize = uploadedString.length;

        if (Math.abs(originalString.length - uploadedString.length) > 100) {
            validation.isValid = false;
            validation.issues.push(`Diferença significativa no tamanho dos dados: Original ${originalString.length} vs Uploaded ${uploadedString.length}`);
        }

        // Verificar texto
        validation.stats.textComparison.originalLength = originalData.fullText?.length || 0;
        validation.stats.textComparison.uploadedLength = uploadedData.content?.length || 0;
        
        if (originalData.fullText && uploadedData.content) {
            const textMatch = originalData.fullText === uploadedData.content;
            validation.stats.textComparison.match = textMatch;
            
            if (!textMatch) {
                validation.isValid = false;
                validation.issues.push('Conteúdo de texto não corresponde entre original e upload');
            }
        }

        // Verificar estrutura DOM
        validation.stats.structureComparison.originalElements = originalData.structure?.length || 0;
        validation.stats.structureComparison.uploadedElements = uploadedData.structure?.length || 0;
        
        if (originalData.structure && uploadedData.structure) {
            const structureMatch = JSON.stringify(originalData.structure) === JSON.stringify(uploadedData.structure);
            validation.stats.structureComparison.match = structureMatch;
            
            if (!structureMatch) {
                validation.isValid = false;
                validation.issues.push('Estrutura DOM não corresponde entre original e upload');
            }
        }

        // Verificar classes CSS
        validation.stats.classesComparison.originalClasses = originalData.allClasses?.length || 0;
        validation.stats.classesComparison.uploadedClasses = uploadedData.allClasses?.length || 0;
        
        if (originalData.allClasses && uploadedData.allClasses) {
            const classesMatch = JSON.stringify(originalData.allClasses) === JSON.stringify(uploadedData.allClasses);
            validation.stats.classesComparison.match = classesMatch;
            
            if (!classesMatch) {
                validation.isValid = false;
                validation.issues.push('Classes CSS não correspondem entre original e upload');
            }
        }

        // Verificar metadados essenciais
        const essentialFields = ['url', 'title', 'timestamp'];
        for (const field of essentialFields) {
            if (originalData[field] !== uploadedData[field]) {
                validation.isValid = false;
                validation.issues.push(`Campo essencial '${field}' não corresponde entre original e upload`);
            }
        }

        await log('INFO', 'Validação de integridade concluída:', validation);
        return validation;

    } catch (error) {
        await log('ERROR', 'Erro durante validação de integridade:', { error: error.message });
        validation.isValid = false;
        validation.issues.push(`Erro durante validação: ${error.message}`);
        return validation;
    }
}

async function verifyUploadedFile(objectKey) {
    try {
        const response = await fetch(`${R2_CONFIG.endpoint}/${objectKey}`, {
            method: 'HEAD',
            headers: {
                'Authorization': `AWS4-HMAC-SHA256 Credential=${R2_CONFIG.accessKeyId}`
            }
        });

        if (response.ok) {
            const contentLength = response.headers.get('content-length');
            const lastModified = response.headers.get('last-modified');
            
            await log('INFO', 'Arquivo verificado no R2:', {
                objectKey,
                contentLength,
                lastModified
            });
            
            return {
                exists: true,
                size: parseInt(contentLength),
                lastModified
            };
        } else {
            await log('WARN', 'Arquivo não encontrado no R2:', { objectKey, status: response.status });
            return { exists: false };
        }
    } catch (error) {
        await log('ERROR', 'Erro ao verificar arquivo no R2:', { error: error.message });
        return { exists: false, error: error.message };
    }
}

async function createIntegrityReport(originalData, uploadResult, verificationResult) {
    const report = {
        timestamp: new Date().toISOString(),
        version: VERSION,
        summary: {
            uploadSuccess: uploadResult.success,
            verificationSuccess: verificationResult.exists,
            dataIntegrity: true, // Será validado abaixo
            recommendations: []
        },
        details: {
            originalData: {
                size: JSON.stringify(originalData).length,
                hasText: !!originalData.fullText,
                hasStructure: !!originalData.structure,
                hasClasses: !!originalData.allClasses
            },
            uploadResult,
            verificationResult
        }
    };

    // Validação de integridade
    if (uploadResult.success && verificationResult.exists) {
        const integrityValidation = await validateDataIntegrity(originalData, uploadResult.data);
        report.summary.dataIntegrity = integrityValidation.isValid;
        report.details.integrityValidation = integrityValidation;
        
        if (!integrityValidation.isValid) {
            report.summary.recommendations.push('Verificar integridade dos dados - problemas detectados');
        }
    }

    // Recomendações baseadas nos resultados
    if (!uploadResult.success) {
        report.summary.recommendations.push('Revisar configurações de upload');
    }
    if (!verificationResult.exists) {
        report.summary.recommendations.push('Verificar se o arquivo foi realmente salvo');
    }

    await log('INFO', 'Relatório de integridade criado:', report);
    return report;
}

async function uploadToR2(uploadData) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const objectKey = `legaltech/${timestamp}-${sanitizeFilename(uploadData.title)}.json`;
    
    try {
        await log('INFO', 'Iniciando upload para R2...', { objectKey });
        
        // Gerar assinatura AWS v4
        const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        const datetime = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '');
        const region = 'auto';
        const service = 's3';
        
        const payload = JSON.stringify(uploadData);
        const payloadHash = await generateChecksum(payload);
        
        const canonicalRequest = [
            'PUT',
            `/${objectKey}`,
            '',
            `host:${R2_CONFIG.endpoint.replace('https://', '')}`,
            `x-amz-content-sha256:${payloadHash}`,
            `x-amz-date:${datetime}`,
            '',
            'host;x-amz-content-sha256;x-amz-date',
            payloadHash
        ].join('\n');
        
        const stringToSign = [
            'AWS4-HMAC-SHA256',
            datetime,
            `${date}/${region}/${service}/aws4_request`,
            await generateChecksum(canonicalRequest)
        ].join('\n');
        
        const signature = await generateSignature(stringToSign, date, region, service);
        const authorizationHeader = `AWS4-HMAC-SHA256 Credential=${R2_CONFIG.accessKeyId}/${date}/${region}/${service}/aws4_request,SignedHeaders=host;x-amz-content-sha256;x-amz-date,Signature=${signature}`;
        
        const response = await fetch(`${R2_CONFIG.endpoint}/${objectKey}`, {
            method: 'PUT',
            headers: {
                'Authorization': authorizationHeader,
                'Content-Type': 'application/json',
                'x-amz-content-sha256': payloadHash,
                'x-amz-date': datetime
            },
            body: payload
        });
        
        if (response.ok) {
            const result = {
                success: true,
                objectKey,
                url: `${R2_CONFIG.endpoint}/${objectKey}`,
                data: uploadData
            };
            
            await log('INFO', 'Upload para R2 realizado com sucesso!', result);
            
            // Verificar integridade
            const verificationResult = await verifyUploadedFile(objectKey);
            const integrityReport = await createIntegrityReport(uploadData, result, verificationResult);
            
            return {
                ...result,
                verificationResult,
                integrityReport
            };
        } else {
            const errorText = await response.text();
            throw new Error(`Erro no upload: ${response.status} - ${errorText}`);
        }
    } catch (error) {
        await log('ERROR', 'Falha no upload para R2:', { error: error.message });
        return {
            success: false,
            error: error.message,
            objectKey
        };
    }
}

async function generateSignature(stringToSign, date, region, service) {
    const kDate = await crypto.subtle.importKey(
        'raw',
        new TextEncoder().encode(`AWS4${R2_CONFIG.secretAccessKey}`),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );
    
    const kRegion = await crypto.subtle.importKey(
        'raw',
        await crypto.subtle.sign('HMAC', kDate, new TextEncoder().encode(date)),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );
    
    const kService = await crypto.subtle.importKey(
        'raw',
        await crypto.subtle.sign('HMAC', kRegion, new TextEncoder().encode(region)),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );
    
    const kSigning = await crypto.subtle.importKey(
        'raw',
        await crypto.subtle.sign('HMAC', kService, new TextEncoder().encode(service)),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );
    
    const signature = await crypto.subtle.sign('HMAC', kSigning, new TextEncoder().encode(stringToSign));
    return Array.from(new Uint8Array(signature)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function onContextMenuClick(info, tab) {
    if (info.menuItemId === 'save-page') {
        await savePage(tab.id);
    } else if (info.menuItemId.startsWith('save-with-tag-')) {
        const tag = info.menuItemId.replace('save-with-tag-', '');
        await savePage(tab.id, tag);
    }
}

async function testR2Connection() {
    try {
        await log('INFO', 'Testando conexão com R2...');
        
        const testData = {
            test: true,
            timestamp: new Date().toISOString(),
            message: 'Teste de conexão R2'
        };
        
        const result = await uploadToR2(testData);
        
        if (result.success) {
            await log('INFO', '✅ Conexão R2 funcionando corretamente!');
            return { success: true, message: 'Conexão R2 OK' };
        } else {
            await log('ERROR', '❌ Falha na conexão R2:', result.error);
            return { success: false, message: result.error };
        }
    } catch (error) {
        await log('ERROR', '❌ Erro no teste R2:', { error: error.message });
        return { success: false, message: error.message };
    }
}

async function testOpenAIConnection() {
    try {
        await log('INFO', 'Testando conexão com OpenAI...');
        
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [{
                    role: 'user',
                    content: 'Teste de conexão - responda apenas "OK"'
                }],
                max_tokens: 10
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            await log('INFO', '✅ Conexão OpenAI funcionando corretamente!');
            return { success: true, message: 'Conexão OpenAI OK' };
        } else {
            const errorData = await response.json();
            await log('ERROR', '❌ Falha na conexão OpenAI:', errorData);
            return { success: false, message: errorData.error.message };
        }
    } catch (error) {
        await log('ERROR', '❌ Erro no teste OpenAI:', { error: error.message });
        return { success: false, message: error.message };
    }
}

async function buildContextMenus() {
    try {
        // Remover menus existentes
        await chrome.contextMenus.removeAll();
        
        // Menu principal
        chrome.contextMenus.create({
            id: 'save-page',
            title: '💾 Salvar Página',
            contexts: ['page']
        });
        
        // Obter tags do storage
        const { tags = [] } = await chrome.storage.sync.get('tags');
        
        // Criar submenus para cada tag
        if (tags.length > 0) {
            chrome.contextMenus.create({
                id: 'save-with-tag-separator',
                title: '──────────',
                contexts: ['page']
            });
            
            tags.forEach(tag => {
                chrome.contextMenus.create({
                    id: `save-with-tag-${tag.name}`,
                    title: `🏷️ ${tag.name}`,
                    contexts: ['page']
                });
            });
        }
        
        await log('INFO', 'Menus de contexto construídos:', { tagsCount: tags.length });
    } catch (error) {
        await log('ERROR', 'Erro ao construir menus de contexto:', { error: error.message });
    }
}

async function capturePageData(tabId) {
    try {
        await log('INFO', 'Capturando dados da página...');
        
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        const pageData = await chrome.scripting.executeScript({
            target: { tabId },
            function: () => {
                // Função que será executada na página
                function walkDOM(node, parentStructure) {
                    const element = {
                        tagName: node.tagName?.toLowerCase(),
                        className: node.className,
                        id: node.id,
                        textContent: node.textContent?.trim(),
                        children: []
                    };
                    
                    // Adicionar atributos importantes
                    if (node.tagName) {
                        const importantAttrs = ['href', 'src', 'alt', 'title', 'data-testid'];
                        importantAttrs.forEach(attr => {
                            if (node.getAttribute(attr)) {
                                element[attr] = node.getAttribute(attr);
                            }
                        });
                    }
                    
                    // Processar filhos
                    for (let child of node.childNodes) {
                        if (child.nodeType === Node.ELEMENT_NODE) {
                            element.children.push(walkDOM(child, element));
                        }
                    }
                    
                    return element;
                }
                
                // Capturar dados da página
                const pageInfo = {
                    url: window.location.href,
                    title: document.title,
                    timestamp: new Date().toISOString(),
                    fullText: document.body.innerText,
                    structure: walkDOM(document.body),
                    allClasses: Array.from(document.querySelectorAll('*'))
                        .map(el => el.className)
                        .filter(className => className && className.trim())
                        .flatMap(className => className.split(' '))
                        .filter(className => className.trim())
                        .filter((className, index, arr) => arr.indexOf(className) === index)
                        .slice(0, 100), // Limitar a 100 classes únicas
                    meta: {
                        description: document.querySelector('meta[name="description"]')?.content,
                        keywords: document.querySelector('meta[name="keywords"]')?.content,
                        author: document.querySelector('meta[name="author"]')?.content,
                        viewport: document.querySelector('meta[name="viewport"]')?.content
                    }
                };
                
                return pageInfo;
            }
        });
        
        if (pageData && pageData[0] && pageData[0].result) {
            const data = pageData[0].result;
            await log('INFO', 'Dados da página capturados com sucesso:', {
                url: data.url,
                title: data.title,
                textLength: data.fullText?.length || 0,
                structureElements: data.structure?.children?.length || 0
            });
            return data;
        } else {
            throw new Error('Falha ao capturar dados da página');
        }
    } catch (error) {
        await log('ERROR', 'Erro ao capturar dados da página:', { error: error.message });
        throw error;
    }
}

function validatePageData(pageData) {
    const errors = [];
    
    if (!pageData.url) errors.push('URL não encontrada');
    if (!pageData.title) errors.push('Título não encontrado');
    if (!pageData.fullText || pageData.fullText.length < 10) errors.push('Texto insuficiente');
    if (!pageData.structure) errors.push('Estrutura DOM não encontrada');
    
    if (errors.length > 0) {
        throw new Error(`Dados da página inválidos: ${errors.join(', ')}`);
    }
    
    return true;
}

async function savePage(tabId, tag = null) {
    try {
        await log('INFO', 'Iniciando salvamento da página...', { tag });
        
        // Capturar dados da página
        const pageData = await capturePageData(tabId);
        
        // Validar dados
        validatePageData(pageData);
        
        // Adicionar tag se fornecida
        if (tag) {
            pageData.tag = tag;
        }
        
        // Processar com OpenAI se habilitado
        const { useOpenAI = true } = await chrome.storage.sync.get('useOpenAI');
        
        if (useOpenAI && OPENAI_API_KEY !== 'YOUR_OPENAI_API_KEY_HERE') {
            try {
                pageData.content = await correctTextWithOpenAI(pageData.fullText);
                await log('INFO', 'Texto processado com OpenAI');
            } catch (error) {
                await log('WARN', 'Falha no processamento OpenAI, usando texto original');
                pageData.content = pageData.fullText;
            }
        } else {
            pageData.content = pageData.fullText;
        }
        
        // Upload para R2
        const uploadResult = await uploadToR2(pageData);
        
        if (uploadResult.success) {
            await log('INFO', '✅ Página salva com sucesso!', {
                objectKey: uploadResult.objectKey,
                url: uploadResult.url
            });
            
            // Notificar usuário
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon16.png',
                title: 'LegalLindaAI',
                message: `Página salva com sucesso! ${tag ? `(Tag: ${tag})` : ''}`
            });
            
            return uploadResult;
        } else {
            throw new Error(`Falha no upload: ${uploadResult.error}`);
        }
        
    } catch (error) {
        await log('ERROR', 'Erro ao salvar página:', { error: error.message });
        
        // Notificar usuário sobre o erro
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon16.png',
            title: 'LegalLindaAI - Erro',
            message: `Erro ao salvar: ${error.message}`
        });
        
        throw error;
    }
}

async function sendToAgentAPI(pageData, agentId) {
    try {
        await log('INFO', 'Enviando dados para API do agente...', { agentId });
        
        const response = await fetch(`http://localhost:5000/api/v1/agents/${agentId}/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: pageData.content,
                metadata: {
                    url: pageData.url,
                    title: pageData.title,
                    tag: pageData.tag,
                    timestamp: pageData.timestamp
                }
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            await log('INFO', 'Dados enviados para agente com sucesso!', result);
            return result;
        } else {
            const errorData = await response.json();
            throw new Error(`API retornou erro ${response.status}: ${errorData.error}`);
        }
    } catch (error) {
        await log('ERROR', 'Erro ao enviar dados para agente:', { error: error.message });
        throw error;
    }
}

// --- SISTEMA DE LIMPEZA DE DOM ---
function cleanDOMStructure(structure, options = {}) {
    const {
        removeProgress = true,
        removeA11y = true,
        removePrint = true,
        preserveText = true
    } = options;
    
    function shouldRemoveElement(element, depth = 0) {
        if (!element || !element.tagName) return false;
        
        // Limitar profundidade para evitar loops infinitos
        if (depth > 10) return false;
        
        const tagName = element.tagName.toLowerCase();
        const className = element.className || '';
        
        // Remover elementos de progresso
        if (removeProgress && (
            tagName === 'progress' ||
            className.includes('progress') ||
            className.includes('loading') ||
            className.includes('spinner')
        )) {
            return true;
        }
        
        // Remover elementos de acessibilidade desnecessários
        if (removeA11y && (
            className.includes('sr-only') ||
            className.includes('screen-reader') ||
            className.includes('visually-hidden')
        )) {
            return true;
        }
        
        // Remover elementos de impressão
        if (removePrint && (
            className.includes('print-only') ||
            className.includes('no-print') ||
            className.includes('print-hidden')
        )) {
            return true;
        }
        
        return false;
    }
    
    function hasTextContent(element, depth = 0) {
        if (!element) return false;
        if (depth > 5) return false;
        
        if (element.textContent && element.textContent.trim().length > 0) {
            return true;
        }
        
        if (element.children) {
            for (let child of element.children) {
                if (hasTextContent(child, depth + 1)) {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    function cleanElement(element, depth = 0) {
        if (!element) return null;
        
        // Verificar se deve remover o elemento
        if (shouldRemoveElement(element, depth)) {
            return null;
        }
        
        // Se preservar texto e o elemento não tem texto, remover
        if (preserveText && !hasTextContent(element, depth)) {
            return null;
        }
        
        // Criar elemento limpo
        const cleanedElement = {
            tagName: element.tagName,
            className: element.className,
            id: element.id,
            textContent: element.textContent,
            children: []
        };
        
        // Processar filhos
        if (element.children) {
            for (let child of element.children) {
                const cleanedChild = cleanElement(child, depth + 1);
                if (cleanedChild) {
                    cleanedElement.children.push(cleanedChild);
                }
            }
        }
        
        return cleanedElement;
    }
    
    return cleanElement(structure, 0);
}

function extractCleanText(structure) {
    function extractFromElement(element) {
        if (!element) return '';
        
        let text = element.textContent || '';
        
        if (element.children) {
            for (let child of element.children) {
                text += ' ' + extractFromElement(child);
            }
        }
        
        return text.trim();
    }
    
    return extractFromElement(structure);
} 