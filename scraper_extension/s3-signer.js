/**
 * S3Signer
 * Classe para gerar assinaturas AWS Signature v4 para o Cloudflare R2.
 * Esta versão corrige a codificação URI para seguir exatamente o padrão AWS.
 */
class S3Signer {
    constructor(config) {
        if (!config || !config.accessKeyId || !config.secretAccessKey || !config.endpoint) {
            throw new Error("Configuração do S3Signer inválida. 'accessKeyId', 'secretAccessKey', e 'endpoint' são obrigatórios.");
        }
        this.accessKeyId = config.accessKeyId;
        this.secretAccessKey = config.secretAccessKey;
        this.endpoint = new URL(config.endpoint);
        this.region = 'auto'; // R2 usa 'auto'
        this.service = 's3';
    }

    /**
     * Codifica uma string para um caminho de URI seguindo o padrão AWS Signature V4.
     * @param {string} string - A string a ser codificada.
     * @returns {string} A string codificada.
     */
    uriEscapePath(string) {
        // AWS Signature V4: codifica todos os caracteres exceto: A-Z, a-z, 0-9, -, _, ., ~, /
        return string.split('/').map(segment => {
            return encodeURIComponent(segment).replace(/[A-Za-z0-9\-_.~]/g, (match) => {
                // Mantém caracteres seguros sem codificação
                return match;
            });
        }).join('/');
    }

    /**
     * Gera os cabeçalhos assinados para uma requisição AWS v4.
     * @param {string} method - O método HTTP (ex: 'PUT', 'GET').
     * @param {string} objectKey - A chave do objeto no bucket (caminho do arquivo).
     * @param {Object} headers - Cabeçalhos da requisição.
     * @param {string|Buffer} body - O corpo da requisição.
     * @returns {Promise<Object>} Um objeto contendo todos os cabeçalhos necessários para a requisição.
     */
    async sign(method, objectKey, headers = {}, body = '') {
        const host = this.endpoint.hostname;
        
        // O caminho canônico DEVE começar com '/' e ser codificado corretamente
        const path = `/${objectKey}`;
        const encodedPath = this.uriEscapePath(path);
        
        const amzDate = new Date().toISOString().replace(/[:-]|\.\d{3}Z$/g, '') + 'Z';
        const dateStamp = amzDate.substring(0, 8);
        const contentSha256 = await this.sha256(body);

        // Cabeçalhos canônicos: todos em lowercase e ordenados
        const canonicalHeaders = {
            'host': host,
            'x-amz-date': amzDate,
            'x-amz-content-sha256': contentSha256,
            ...Object.fromEntries(Object.entries(headers).map(([k, v]) => [k.toLowerCase(), v.trim()]))
        };

        const sortedHeaderKeys = Object.keys(canonicalHeaders).sort();
        const canonicalHeadersStr = sortedHeaderKeys.map(k => `${k}:${canonicalHeaders[k]}`).join('\n') + '\n';
        const signedHeadersStr = sortedHeaderKeys.join(';');

        const canonicalRequest = [
            method,
            encodedPath, // Caminho codificado corretamente
            '', // queryString (vazio)
            canonicalHeadersStr,
            signedHeadersStr,
            contentSha256
        ].join('\n');

        const credentialScope = `${dateStamp}/${this.region}/${this.service}/aws4_request`;
        const stringToSign = [
            'AWS4-HMAC-SHA256',
            amzDate,
            credentialScope,
            await this.sha256(canonicalRequest)
        ].join('\n');

        const signature = await this.createSignature(this.secretAccessKey, dateStamp, this.region, this.service, stringToSign);
        const authorizationHeader = `AWS4-HMAC-SHA256 Credential=${this.accessKeyId}/${credentialScope}, SignedHeaders=${signedHeadersStr}, Signature=${signature}`;

        return {
            ...headers,
            'Authorization': authorizationHeader,
            'X-Amz-Content-Sha256': contentSha256,
            'X-Amz-Date': amzDate,
        };
    }

    async sha256(message) {
        const msgBuffer = new TextEncoder().encode(message);
        const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    async createSignature(secret, date, region, service, stringToSign) {
        const kSecret = `AWS4${secret}`;
        const kDate = await this.hmac(kSecret, date);
        const kRegion = await this.hmac(kDate, region);
        const kService = await this.hmac(kRegion, service);
        const kSigning = await this.hmac(kService, 'aws4_request');
        return await this.hmac(kSigning, stringToSign, 'hex');
    }

    async hmac(key, message, format = 'binary') {
        const keyBuffer = typeof key === 'string' ? new TextEncoder().encode(key) : key;
        const cryptoKey = await crypto.subtle.importKey('raw', keyBuffer, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
        const messageBuffer = new TextEncoder().encode(message);
        const signature = await crypto.subtle.sign('HMAC', cryptoKey, messageBuffer);
        if (format === 'hex') {
            return Array.from(new Uint8Array(signature)).map(b => b.toString(16).padStart(2, '0')).join('');
        }
        return signature;
    }
} 