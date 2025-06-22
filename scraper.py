import asyncio
import logging
import re
import random
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Comment

# Importações para integração OpenAI
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Limpa e normaliza o texto extraído, removendo elementos desnecessários.
    """
    if not text:
        return ""
    
    # Remover padrões CSS comuns
    css_patterns = [
        r'--[a-zA-Z-]+:\s*[^;]+;',  # Variáveis CSS
        r'[a-zA-Z-]+:\s*[^;]+;',    # Propriedades CSS
        r'@[a-zA-Z-]+[^{]*{[^}]*}', # At-rules CSS
        r'\.[\w-]+\s*{[^}]*}',      # Classes CSS
        r'#[\w-]+\s*{[^}]*}',       # IDs CSS
        r'[\w-]+\s*:\s*[\w\s\(\),-]+;', # Propriedades CSS genéricas
        r'rgb\([^)]+\)',            # Cores RGB
        r'rgba\([^)]+\)',           # Cores RGBA
        r'#[0-9a-fA-F]{3,8}',       # Cores hexadecimais
        r'px|em|rem|%|vh|vw|pt',    # Unidades CSS
        r'font-family|font-size|font-weight|color|background|margin|padding|border|width|height', # Propriedades comuns
    ]
    
    for pattern in css_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remover múltiplas quebras de linha e espaços
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s*{\s*', ' ', text)
    text = re.sub(r'\s*}\s*', ' ', text)
    
    # Remover linhas que são apenas pontuação ou caracteres especiais
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Filtrar linhas que parecem ser CSS ou código
        if (line and 
            len(line) > 3 and 
            not re.match(r'^[\{\}\[\]\(\):;,\-\s]*$', line) and
            not re.match(r'^[a-zA-Z-]+:\s*.*$', line) and  # Propriedades CSS
            not re.match(r'^--[a-zA-Z-]+:', line) and      # Variáveis CSS
            not re.match(r'^\.[a-zA-Z-]', line) and        # Classes CSS
            not re.match(r'^#[a-zA-Z-]', line) and         # IDs CSS
            not ':' in line[:20] or ' ' in line[:20]):     # Evitar propriedades CSS
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_main_content_from_html(html_content: str) -> dict:
    """
    Extrai múltiplas versões do conteúdo do HTML para posterior processamento.
    Retorna um dicionário com diferentes extrações.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remover elementos que nunca contêm conteúdo útil
    unwanted_elements = [
        'script', 'style', 'noscript', 'iframe', 'embed', 'object', 'svg',
        'meta', 'link', 'title', 'base', 'area', 'map'
    ]
    
    for selector in unwanted_elements:
        for element in soup.select(selector):
            element.decompose()
    
    # Remover comentários HTML
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Extrair diferentes tipos de conteúdo
    content_extractions = {
        'title': soup.title.get_text(strip=True) if soup.title else "",
        'meta_description': "",
        'headings': [],
        'paragraphs': [],
        'lists': [],
        'semantic_content': "",
        'full_body_text': "",
        'jurisprudence_content': ""  # Específico para sites jurídicos
    }
    
    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        content_extractions['meta_description'] = meta_desc.get('content', '')
    
    # Extrair headings (h1-h6)
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = heading.get_text(strip=True)
        if text and len(text) > 2:
            content_extractions['headings'].append({
                'level': heading.name,
                'text': text
            })
    
    # Extrair parágrafos
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text and len(text) > 10:
            content_extractions['paragraphs'].append(text)
    
    # Extrair listas
    for ul in soup.find_all(['ul', 'ol']):
        items = []
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            if text and len(text) > 3:
                items.append(text)
        if items:
            content_extractions['lists'].append(items)
    
    # Extrair conteúdo semântico (main, article, section)
    semantic_selectors = [
        'main', 'article', 'section',
        '[role="main"]', '.content', '.main-content',
        '.article-content', '.post-content', '.entry-content'
    ]
    
    semantic_texts = []
    for selector in semantic_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator='\n', strip=True)
            if text and len(text) > 50:
                semantic_texts.append(text)
    
    content_extractions['semantic_content'] = '\n\n'.join(semantic_texts)
    
    # Extrair conteúdo jurídico específico
    jurisprudence_selectors = [
        '.jurisprudencia-content', '.decisao-content', '.ementa',
        '.acordao', '.sentenca', '.voto', '.relatorio', '.fundamentacao',
        '.tribunal', '.processo', '.julgamento', '.decisao'
    ]
    
    jurisprudence_texts = []
    for selector in jurisprudence_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator='\n', strip=True)
            if text and len(text) > 20:
                jurisprudence_texts.append(text)
    
    content_extractions['jurisprudence_content'] = '\n\n'.join(jurisprudence_texts)
    
    # Extrair texto completo do body como fallback
    if soup.body:
        content_extractions['full_body_text'] = soup.body.get_text(separator='\n', strip=True)
    
    return content_extractions

def process_content_extractions(extractions: dict, url: str, protected: bool = False) -> str:
    """
    Processa as extrações de conteúdo e retorna o texto limpo final.
    Versão melhorada para sites premium.
    """
    # Detectar se é site premium
    is_premium = any(domain in url.lower() for domain in [
        'thomsonreuters', 'westlaw', 'lexisnexis', 'vlex', 'proview'
    ])
    
    # Para sites premium, tentar estratégias mais agressivas primeiro
    if is_premium:
        logger.info("🏢 Processando site premium")
        
        # Tentar usar qualquer conteúdo disponível, mesmo que pequeno
        content_candidates = [
            ('jurisprudence_content', "⚖️ Conteúdo jurídico premium"),
            ('semantic_content', "📄 Conteúdo semântico premium"), 
            ('full_body_text', "🌐 Texto completo premium"),
            ('paragraphs', "📝 Parágrafos premium")
        ]
        
        for key, description in content_candidates:
            content = extractions.get(key, '')
            if isinstance(content, list):
                content = '\n\n'.join(content)
            
            if content and len(content.strip()) > 50:  # Limiar mais baixo para premium
                logger.info(description)
                main_content = content
                break
        else:
            # Se não encontrou conteúdo, tentar headings
            if extractions.get('headings'):
                headings_text = '\n'.join([h.get('text', '') if isinstance(h, dict) else str(h) 
                                         for h in extractions['headings']])
                if len(headings_text.strip()) > 20:
                    logger.info("📋 Usando headings de site premium")
                    main_content = headings_text
                else:
                    main_content = None
            else:
                main_content = None
    else:
        # Lógica normal para sites não-premium
        # Priorizar conteúdo jurídico se disponível
        if extractions['jurisprudence_content'] and len(extractions['jurisprudence_content'].strip()) > 100:
            main_content = extractions['jurisprudence_content']
            logger.info("🏛️ Usando conteúdo jurídico específico")
        
        # Senão, usar conteúdo semântico
        elif extractions['semantic_content'] and len(extractions['semantic_content'].strip()) > 200:
            main_content = extractions['semantic_content']
            logger.info("📄 Usando conteúdo semântico")
        
        # Combinar parágrafos se necessário
        elif extractions['paragraphs'] and len(extractions['paragraphs']) > 2:
            main_content = '\n\n'.join(extractions['paragraphs'])
            logger.info("📝 Usando parágrafos combinados")
        
        # Usar texto completo do body como último recurso
        elif extractions['full_body_text'] and len(extractions['full_body_text'].strip()) > 100:
            main_content = extractions['full_body_text']
            logger.info("🌐 Usando texto completo do body")
        
        else:
            main_content = None
    
    # Se não há conteúdo suficiente
    if not main_content:
        basic_info = f"Título: {extractions['title']}\nURL: {url}\n\n"
        
        if is_premium:
            basic_info += "⚠️ Site premium detectado - Conteúdo pode estar protegido por autenticação.\n"
            basic_info += "Possíveis causas:\n"
            basic_info += "- Conteúdo requer login/assinatura\n"
            basic_info += "- JavaScript complexo não executado completamente\n"
            basic_info += "- Proteção anti-scraping avançada\n"
            basic_info += "- Conteúdo carregado dinamicamente via AJAX\n\n"
            basic_info += "Sugestão: Verificar se o acesso direto à URL funciona no navegador.\n\n"
        elif protected:
            basic_info += "⚠️ Esta página está protegida e não permitiu extração automática de conteúdo.\n"
            basic_info += "Para acessar o conteúdo, visite a URL diretamente no navegador.\n\n"
        else:
            basic_info += "⚠️ Conteúdo textual não pôde ser extraído desta página.\n"
            basic_info += "Possíveis causas: conteúdo gerado por JavaScript, proteção anti-bot, ou estrutura complexa.\n\n"
        
        # Adicionar headings se disponíveis
        if extractions['headings']:
            basic_info += "Títulos encontrados:\n"
            for heading in extractions['headings'][:5]:  # Máximo 5 títulos
                heading_text = heading.get('text', '') if isinstance(heading, dict) else str(heading)
                if heading_text.strip():
                    basic_info += f"- {heading_text}\n"
        
        return basic_info
    
    # Limpar o conteúdo selecionado
    cleaned_content = clean_text(main_content)
    
    # Filtros adicionais para sites protegidos
    if cleaned_content:
        blocked_phrases = [
            'verifying you are human', 'just a moment', 'please wait',
            'checking your browser', 'ddos protection', 'cloudflare',
            'ray id', 'performance & security by', 'enable javascript',
            'browser does not support', 'cookies must be enabled'
        ]
        
        lines = cleaned_content.split('\n')
        final_lines = []
        
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Verificar se a linha não contém frases de bloqueio
            is_blocked = any(phrase in line_lower for phrase in blocked_phrases)
            
            if (line and 
                len(line) > 5 and
                not is_blocked and
                not any(css_word in line_lower for css_word in [
                    'css', 'style', 'font-family', 'color:', 'background',
                    'margin:', 'padding:', 'border:', 'width:', 'height:',
                    'rgba(', 'rgb(', '--', 'px', 'em', 'rem', '%'
                ]) and
                not re.match(r'^[{}:;,\s]*$', line)):
                final_lines.append(line)
        
        cleaned_content = '\n'.join(final_lines)
    
    return cleaned_content

async def human_like_behavior(page):
    """
    Simula comportamento humano para evitar detecção por sistemas anti-bot.
    """
    # Movimento aleatório do mouse
    await page.mouse.move(
        random.randint(100, 800), 
        random.randint(100, 600)
    )
    
    # Scroll aleatório
    await page.evaluate(f"window.scrollTo(0, {random.randint(100, 500)})")
    await page.wait_for_timeout(random.randint(500, 1500))
    
    # Mais um scroll
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await page.wait_for_timeout(random.randint(1000, 2000))

async def detect_cloudflare_protection(page):
    """
    Detecta se a página tem proteção Cloudflare ativa.
    """
    try:
        # Verificar indicadores comuns de Cloudflare
        cloudflare_indicators = [
            'Verifying you are human',
            'Just a moment',
            'Please wait',
            'Checking your browser',
            'DDoS protection',
            'Ray ID',
            'cf-ray',
            'cloudflare'
        ]
        
        page_content = await page.content()
        page_text = await page.inner_text('body') if await page.query_selector('body') else ""
        
        for indicator in cloudflare_indicators:
            if indicator.lower() in page_content.lower() or indicator.lower() in page_text.lower():
                return True
                
        # Verificar elementos específicos do Cloudflare
        cf_selectors = [
            '[data-ray]',
            '.cf-error-details',
            '.cf-wrapper',
            '#cf-content',
            '.cf-browser-verification'
        ]
        
        for selector in cf_selectors:
            if await page.query_selector(selector):
                return True
                
        return False
        
    except Exception:
        return False

async def scrape_url_to_json(url: str) -> dict:
    """
    Captura uma página e retorna todos os dados em formato JSON para posterior processamento.
    Versão melhorada para sites com muito JavaScript.
    """
    logger.info(f"🔍 Iniciando captura JSON da URL: {url}")
    
    try:
        async with async_playwright() as p:
            # Configurar browser com flags anti-detecção
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-automation',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-field-trial-config',
                    '--disable-back-forward-cache',
                    '--disable-ipc-flooding-protection',
                    '--enable-javascript',  # Garantir que JS está habilitado
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                ]
            )
            
            # Criar contexto com configurações realistas
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                permissions=['geolocation'],
                java_script_enabled=True,  # Explicitamente habilitar JavaScript
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            page = await context.new_page()
            
            # Mascarar propriedades que indicam automação
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
                
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' }),
                    }),
                });
            """)
            
            # Para sites premium, permitir mais recursos
            is_premium_site = any(domain in url.lower() for domain in [
                'thomsonreuters', 'westlaw', 'lexisnexis', 'vlex', 'proview'
            ])
            
            if is_premium_site:
                # Para sites premium, permitir CSS e outros recursos
                await page.route("**/*", lambda route: (
                    route.abort() if route.request.resource_type in [
                        "image", "font", "media"
                    ] else route.continue_()
                ))
                logger.info("🏢 Site premium detectado - permitindo mais recursos")
            else:
                # Para sites normais, bloquear mais recursos
                await page.route("**/*", lambda route: (
                    route.abort() if route.request.resource_type in [
                        "image", "font", "media"
                    ] else route.continue_()
                ))
            
            # Delay inicial aleatório
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            # Navegar para a página
            logger.info(f"🌐 Navegando para: {url}")
            await page.goto(url, timeout=45000, wait_until='networkidle')  # Aguardar rede idle
            
            # Aguardar carregamento inicial mais longo para sites JS-heavy
            await page.wait_for_timeout(random.randint(5000, 8000))
            
            # Verificar se há proteção Cloudflare
            has_cloudflare = await detect_cloudflare_protection(page)
            
            if has_cloudflare:
                logger.warning(f"🛡️ Proteção Cloudflare detectada em {url}")
                
                # Tentar aguardar mais tempo para verificação automática
                logger.info("⏳ Aguardando verificação automática...")
                await page.wait_for_timeout(random.randint(10000, 15000))
                
                # Simular comportamento humano
                await human_like_behavior(page)
                
                # Aguardar mais um pouco
                await page.wait_for_timeout(random.randint(5000, 10000))
                
                # Verificar novamente se ainda há proteção
                has_cloudflare = await detect_cloudflare_protection(page)
                
                if has_cloudflare:
                    logger.warning(f"🚫 Não foi possível contornar a proteção de {url}")
            
            # Para sites premium, tentar executar JavaScript adicional
            if is_premium_site:
                logger.info("🔧 Executando JavaScript adicional para site premium...")
                
                # Tentar forçar carregamento de conteúdo
                try:
                    await page.evaluate("""
                        // Scroll para ativar lazy loading
                        window.scrollTo(0, document.body.scrollHeight / 2);
                        
                        // Aguardar um pouco
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        
                        // Tentar clicar em elementos que podem carregar conteúdo
                        const buttons = document.querySelectorAll('button, [role="button"], .load-more, .show-more');
                        for (let btn of buttons) {
                            if (btn.textContent && btn.textContent.toLowerCase().includes('load')) {
                                btn.click();
                                break;
                            }
                        }
                        
                        // Aguardar mais um pouco
                        await new Promise(resolve => setTimeout(resolve, 3000));
                    """)
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao executar JavaScript adicional: {e}")
            
            # Simular mais comportamento humano
            await human_like_behavior(page)
            
            # Aguardar conteúdo dinâmico - mais tempo para sites premium
            wait_time = random.randint(8000, 12000) if is_premium_site else random.randint(3000, 6000)
            await page.wait_for_timeout(wait_time)
            
            # Tentar aguardar por seletores específicos de conteúdo
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '.main-content',
                '.document-content', '.legal-content', '.case-content', '.text-content'
            ]
            
            for selector in content_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    logger.info(f"✅ Conteúdo encontrado: {selector}")
                    break
                except:
                    continue
            
            # Extrair todos os dados
            title = await page.title()
            html_content = await page.content()
            current_url = page.url
            
            await browser.close()
            
            # Criar objeto JSON com todos os dados
            page_data = {
                'capture_info': {
                    'original_url': url,
                    'final_url': current_url,
                    'timestamp': datetime.now().isoformat(),
                    'protected': has_cloudflare,
                    'is_premium_site': is_premium_site,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                },
                'page_metadata': {
                    'title': title,
                    'html_length': len(html_content)
                },
                'raw_html': html_content,
                'content_extractions': extract_main_content_from_html(html_content)
            }
            
            logger.info(f"📦 Dados JSON capturados - Título: '{title}' | HTML: {len(html_content)} chars")
            
            return {
                "success": True,
                "data": page_data
            }
            
    except Exception as e:
        error_msg = f"Erro ao capturar JSON da URL {url}: {str(e)}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        return {
            "success": False,
            "error": error_msg,
            "url": url
        }

def process_json_to_clean_text(json_data: dict) -> dict:
    """
    Processa os dados JSON e retorna apenas o texto limpo.
    """
    if not json_data.get('success'):
        return json_data
    
    try:
        page_data = json_data['data']
        capture_info = page_data['capture_info']
        extractions = page_data['content_extractions']
        
        # Processar extrações para texto limpo
        clean_content = process_content_extractions(
            extractions, 
            capture_info['original_url'], 
            capture_info['protected']
        )
        
        # Validar conteúdo final
        if not clean_content.strip() or len(clean_content.strip()) < 30:
            clean_content = f"Página: {page_data['page_metadata']['title']}\n"
            clean_content += f"URL: {capture_info['original_url']}\n\n"
            clean_content += "⚠️ Conteúdo textual limitado extraído desta página.\n"
        
        result = {
            "success": True,
            "title": page_data['page_metadata']['title'],
            "content": clean_content,
            "url": capture_info['original_url'],
            "content_length": len(clean_content),
            "protected": capture_info['protected'],
            "capture_timestamp": capture_info['timestamp']
        }
        
        logger.info(f"✅ Processamento JSON concluído - Conteúdo: {len(clean_content)} caracteres")
        return result
        
    except Exception as e:
        error_msg = f"Erro ao processar JSON: {str(e)}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        return {
            "success": False,
            "error": error_msg
        }

async def scrape_url_content(url: str) -> dict:
    """
    Função principal que captura para JSON e depois processa para texto limpo.
    """
    # Primeiro: capturar tudo em JSON
    json_result = await scrape_url_to_json(url)
    
    if not json_result['success']:
        return json_result
    
    # Segundo: processar JSON para texto limpo
    final_result = process_json_to_clean_text(json_result)
    
    return final_result

def scrape_url(url: str) -> dict:
    """Função síncrona que envolve a função assíncrona scrape_url_content."""
    return asyncio.run(scrape_url_content(url))

def save_page_as_json(url: str, filename: str = None) -> dict:
    """
    Salva uma página como JSON para análise posterior.
    """
    json_result = asyncio.run(scrape_url_to_json(url))
    
    if json_result['success'] and filename:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_result['data'], f, ensure_ascii=False, indent=2)
            logger.info(f"💾 JSON salvo em: {filename}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar JSON: {e}")
    
    return json_result

def process_saved_json(filename: str) -> dict:
    """
    Processa um arquivo JSON salvo e extrai o texto limpo.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            page_data = json.load(f)
        
        json_result = {"success": True, "data": page_data}
        return process_json_to_clean_text(json_result)
        
    except Exception as e:
        error_msg = f"Erro ao processar arquivo JSON {filename}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

def test_scraper():
    """Função para testar o scraper com diferentes tipos de sites."""
    test_urls = [
        'https://www.example.com',
        'https://www.jusbrasil.com.br/jurisprudencia/trt-4/922418931',
        'https://pt.wikipedia.org/wiki/Intelig%C3%AAncia_artificial'
    ]
    
    for url in test_urls:
        print(f"\n{'='*70}")
        print(f"🧪 Testando SCRAPER JSON->TEXTO: {url}")
        print('='*70)
        
        result = scrape_url(url)
        
        if result['success']:
            print(f"✅ Sucesso!")
            print(f"📄 Título: {result['title']}")
            print(f"📏 Tamanho do conteúdo: {result['content_length']} caracteres")
            if result.get('protected'):
                print(f"🛡️ Página protegida detectada")
            print(f"📝 Prévia do conteúdo (400 chars):")
            print("-" * 50)
            print(f"{result['content'][:400]}...")
            print("-" * 50)
        else:
            print(f"❌ Erro: {result['error']}")

def chunk_text_with_openai(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Divide o texto em chunks usando RecursiveCharacterTextSplitter e prepara para embeddings.
    
    Args:
        text: Texto a ser dividido
        chunk_size: Tamanho máximo de cada chunk
        chunk_overlap: Sobreposição entre chunks
        
    Returns:
        Lista de documentos LangChain prontos para embeddings
    """
    try:
        # Configurar o text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Parágrafos
                "\n",    # Linhas
                ".",     # Sentenças
                "!",     # Exclamações
                "?",     # Perguntas
                ";",     # Ponto e vírgula
                ",",     # Vírgulas
                " ",     # Espaços
                ""       # Caracteres individuais
            ]
        )
        
        # Dividir o texto em chunks
        chunks = text_splitter.split_text(text)
        
        # Converter em documentos LangChain
        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Apenas chunks não vazios
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "total_chunks": len(chunks),
                        "source": "web_scraper",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                documents.append(doc)
        
        logger.info(f"📄 Texto dividido em {len(documents)} chunks (tamanho: {chunk_size}, overlap: {chunk_overlap})")
        return documents
        
    except Exception as e:
        logger.error(f"❌ Erro ao dividir texto em chunks: {e}")
        return []

def generate_embeddings_with_openai(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """
    Gera embeddings usando a API da OpenAI.
    
    Args:
        texts: Lista de textos para gerar embeddings
        model: Modelo de embedding da OpenAI
        
    Returns:
        Lista de embeddings (vetores)
    """
    try:
        # Verificar se a API key está configurada
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("❌ OPENAI_API_KEY não configurada")
            return []
        
        # Inicializar cliente OpenAI
        client = OpenAI(api_key=api_key)
        
        # Filtrar textos vazios
        valid_texts = [text.strip() for text in texts if text.strip()]
        if not valid_texts:
            logger.warning("⚠️ Nenhum texto válido para gerar embeddings")
            return []
        
        logger.info(f"🔮 Gerando embeddings para {len(valid_texts)} textos usando modelo {model}")
        
        # Gerar embeddings
        response = client.embeddings.create(
            input=valid_texts,
            model=model
        )
        
        # Extrair os vetores
        embeddings = [embedding.embedding for embedding in response.data]
        
        logger.info(f"✅ {len(embeddings)} embeddings gerados com sucesso")
        return embeddings
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar embeddings: {e}")
        return []

def process_scraped_content_for_rag(scraped_result: dict, 
                                   chunk_size: int = 1000, 
                                   chunk_overlap: int = 200,
                                   generate_embeddings: bool = True) -> dict:
    """
    Processa o conteúdo extraído pelo scraper para uso no sistema RAG.
    
    Args:
        scraped_result: Resultado do scraper
        chunk_size: Tamanho dos chunks
        chunk_overlap: Sobreposição entre chunks
        generate_embeddings: Se deve gerar embeddings
        
    Returns:
        Dicionário com chunks e embeddings processados
    """
    try:
        if not scraped_result.get('success'):
            return {
                "success": False,
                "error": scraped_result.get('error', 'Scraping falhou'),
                "chunks": [],
                "embeddings": []
            }
        
        content = scraped_result.get('content', '')
        if not content.strip():
            return {
                "success": False,
                "error": "Conteúdo vazio",
                "chunks": [],
                "embeddings": []
            }
        
        logger.info(f"🔄 Processando conteúdo para RAG: {len(content)} caracteres")
        
        # 1. Dividir em chunks
        documents = chunk_text_with_openai(content, chunk_size, chunk_overlap)
        
        if not documents:
            return {
                "success": False,
                "error": "Falha ao dividir texto em chunks",
                "chunks": [],
                "embeddings": []
            }
        
        # 2. Preparar dados dos chunks
        chunks_data = []
        chunk_texts = []
        
        for doc in documents:
            chunk_info = {
                "text": doc.page_content,
                "metadata": doc.metadata,
                "length": len(doc.page_content)
            }
            chunks_data.append(chunk_info)
            chunk_texts.append(doc.page_content)
        
        # 3. Gerar embeddings se solicitado
        embeddings = []
        if generate_embeddings:
            logger.info("🔮 Gerando embeddings para os chunks...")
            embeddings = generate_embeddings_with_openai(chunk_texts)
            
            if len(embeddings) != len(chunk_texts):
                logger.warning(f"⚠️ Número de embeddings ({len(embeddings)}) diferente do número de chunks ({len(chunk_texts)})")
        
        # 4. Combinar chunks com embeddings
        for i, chunk in enumerate(chunks_data):
            if i < len(embeddings):
                chunk["embedding"] = embeddings[i]
                chunk["embedding_dimensions"] = len(embeddings[i])
            else:
                chunk["embedding"] = None
                chunk["embedding_dimensions"] = 0
        
        result = {
            "success": True,
            "source_url": scraped_result.get('url', ''),
            "source_title": scraped_result.get('title', ''),
            "original_content_length": len(content),
            "total_chunks": len(chunks_data),
            "chunks": chunks_data,
            "embeddings": embeddings,
            "processing_info": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embedding_model": "text-embedding-3-small",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ Processamento RAG concluído: {len(chunks_data)} chunks, {len(embeddings)} embeddings")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar conteúdo para RAG: {e}")
        return {
            "success": False,
            "error": str(e),
            "chunks": [],
            "embeddings": []
        }

def scrape_and_process_for_rag(url: str, 
                              chunk_size: int = 1000, 
                              chunk_overlap: int = 200) -> dict:
    """
    Função completa que faz scraping de uma URL e processa para RAG.
    
    Args:
        url: URL para fazer scraping
        chunk_size: Tamanho dos chunks
        chunk_overlap: Sobreposição entre chunks
        
    Returns:
        Dicionário com conteúdo processado para RAG
    """
    logger.info(f"🚀 Iniciando scraping e processamento RAG para: {url}")
    
    # 1. Fazer scraping
    scraped_result = scrape_url(url)
    
    # 2. Processar para RAG
    rag_result = process_scraped_content_for_rag(
        scraped_result, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    # 3. Adicionar informações do scraping
    if rag_result.get('success'):
        rag_result['scraping_info'] = {
            "url": scraped_result.get('url', ''),
            "title": scraped_result.get('title', ''),
            "content_length": scraped_result.get('content_length', 0),
            "protected": scraped_result.get('protected', False),
            "capture_timestamp": scraped_result.get('capture_timestamp', '')
        }
    
    return rag_result

def save_rag_processed_content(rag_result: dict, filename: str = None) -> dict:
    """
    Salva o conteúdo processado para RAG em arquivo JSON.
    
    Args:
        rag_result: Resultado do processamento RAG
        filename: Nome do arquivo (opcional)
        
    Returns:
        Resultado da operação de salvamento
    """
    try:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            url_clean = re.sub(r'[^\w\-_\.]', '_', rag_result.get('source_url', 'unknown'))[:50]
            filename = f"rag_processed_{url_clean}_{timestamp}.json"
        
        # Salvar sem os embeddings para arquivo mais leve (embeddings são grandes)
        save_data = rag_result.copy()
        if 'embeddings' in save_data:
            save_data['embeddings_count'] = len(save_data['embeddings'])
            del save_data['embeddings']  # Remover embeddings do arquivo
        
        # Remover embeddings dos chunks também
        if 'chunks' in save_data:
            for chunk in save_data['chunks']:
                if 'embedding' in chunk:
                    chunk['has_embedding'] = chunk['embedding'] is not None
                    del chunk['embedding']
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Conteúdo RAG salvo em: {filename}")
        return {
            "success": True,
            "filename": filename,
            "chunks_saved": len(save_data.get('chunks', [])),
            "embeddings_generated": save_data.get('embeddings_count', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar conteúdo RAG: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def test_openai_integration():
    """Testa a integração com OpenAI para chunking e embeddings."""
    print("\n🧪 Testando Integração OpenAI - Chunking e Embeddings")
    print("=" * 60)
    
    # Testar com uma URL
    test_url = "https://www.example.com"
    print(f"\n1. Testando scraping + RAG processing: {test_url}")
    
    result = scrape_and_process_for_rag(test_url, chunk_size=500, chunk_overlap=100)
    
    if result['success']:
        print(f"✅ Processamento concluído!")
        print(f"📄 URL: {result['scraping_info']['url']}")
        print(f"📝 Título: {result['scraping_info']['title']}")
        print(f"📏 Conteúdo original: {result['original_content_length']} caracteres")
        print(f"🧩 Total de chunks: {result['total_chunks']}")
        print(f"🔮 Embeddings gerados: {len(result['embeddings'])}")
        
        # Mostrar exemplo de chunk
        if result['chunks']:
            first_chunk = result['chunks'][0]
            print(f"\n📋 Exemplo do primeiro chunk:")
            print(f"   Tamanho: {first_chunk['length']} caracteres")
            print(f"   Texto: {first_chunk['text'][:200]}...")
            if first_chunk.get('embedding'):
                print(f"   Embedding: {len(first_chunk['embedding'])} dimensões")
        
        # Salvar resultado
        save_result = save_rag_processed_content(result)
        if save_result['success']:
            print(f"💾 Salvo em: {save_result['filename']}")
    else:
        print(f"❌ Erro: {result['error']}")

def integrate_with_existing_rag_system(url: str, 
                                       agent_id: str,
                                       chunk_size: int = 1000, 
                                       chunk_overlap: int = 200) -> dict:
    """
    Integra o scraper com o sistema RAG existente do projeto.
    Faz scraping, chunking, embeddings e salva no banco PostgreSQL.
    
    Args:
        url: URL para fazer scraping
        agent_id: ID do agente para isolamento de segurança
        chunk_size: Tamanho dos chunks
        chunk_overlap: Sobreposição entre chunks
        
    Returns:
        Resultado da integração completa
    """
    try:
        logger.info(f"🔗 Iniciando integração RAG completa para agente {agent_id}")
        
        # 1. Fazer scraping e processamento RAG
        rag_result = scrape_and_process_for_rag(url, chunk_size, chunk_overlap)
        
        if not rag_result['success']:
            return {
                "success": False,
                "error": f"Falha no scraping: {rag_result['error']}",
                "agent_id": agent_id,
                "url": url
            }
        
        # 2. Preparar documentos para o sistema existente
        try:
            from vector_store import PGVectorStore
            from langchain.schema import Document
            
            # Criar documentos LangChain com metadados completos
            documents = []
            for i, chunk in enumerate(rag_result['chunks']):
                doc = Document(
                    page_content=chunk['text'],
                    metadata={
                        "source": url,
                        "title": rag_result['source_title'],
                        "chunk_index": i,
                        "total_chunks": rag_result['total_chunks'],
                        "chunk_size": chunk['length'],
                        "url": url,
                        "agent_id": agent_id,
                        "scraping_timestamp": rag_result['scraping_info']['capture_timestamp'],
                        "processing_timestamp": rag_result['processing_info']['timestamp'],
                        "embedding_model": rag_result['processing_info']['embedding_model']
                    }
                )
                documents.append(doc)
            
            # 3. Salvar no sistema RAG existente
            vector_store = PGVectorStore(agent_id=agent_id)
            vector_store.add_documents(documents)
            
            logger.info(f"✅ Integração RAG concluída: {len(documents)} chunks salvos no banco para agente {agent_id}")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "url": url,
                "title": rag_result['source_title'],
                "chunks_saved": len(documents),
                "embeddings_generated": len(rag_result['embeddings']),
                "original_content_length": rag_result['original_content_length'],
                "processing_info": rag_result['processing_info'],
                "scraping_info": rag_result['scraping_info']
            }
            
        except ImportError as e:
            logger.error(f"❌ Erro ao importar sistema RAG existente: {e}")
            return {
                "success": False,
                "error": f"Sistema RAG não disponível: {e}",
                "agent_id": agent_id,
                "url": url,
                "rag_data": rag_result  # Retornar dados processados mesmo assim
            }
            
    except Exception as e:
        logger.error(f"❌ Erro na integração RAG: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent_id": agent_id,
            "url": url
        }

def test_full_rag_integration():
    """Testa a integração completa com o sistema RAG existente."""
    print("\n🧪 Testando Integração Completa com Sistema RAG")
    print("=" * 60)
    
    # ID de agente de teste (usar um existente ou criar um novo)
    test_agent_id = "ae80adff-3ebd-4bc5-afbf-6e739df6d2fb"  # Agente existente do sistema
    test_url = "https://www.example.com"
    
    print(f"\n1. Testando integração completa:")
    print(f"   Agente: {test_agent_id}")
    print(f"   URL: {test_url}")
    
    result = integrate_with_existing_rag_system(
        url=test_url,
        agent_id=test_agent_id,
        chunk_size=600,
        chunk_overlap=100
    )
    
    if result['success']:
        print(f"✅ Integração bem-sucedida!")
        print(f"📄 Título: {result['title']}")
        print(f"🧩 Chunks salvos: {result['chunks_saved']}")
        print(f"🔮 Embeddings gerados: {result['embeddings_generated']}")
        print(f"📏 Conteúdo original: {result['original_content_length']} caracteres")
        print(f"🏷️ Agente: {result['agent_id']}")
        
        # Testar busca no sistema RAG
        try:
            from vector_store import PGVectorStore
            vector_store = PGVectorStore(agent_id=test_agent_id)
            
            # Fazer uma busca de teste
            search_results = vector_store.similarity_search("example domain", k=3)
            print(f"\n🔍 Teste de busca:")
            print(f"   Query: 'example domain'")
            print(f"   Resultados encontrados: {len(search_results)}")
            
            if search_results:
                print(f"   Primeiro resultado: {search_results[0].page_content[:100]}...")
                
        except Exception as e:
            print(f"⚠️ Erro no teste de busca: {e}")
    else:
        print(f"❌ Falha na integração: {result['error']}")
        if 'rag_data' in result:
            print(f"📊 Dados RAG disponíveis: {result['rag_data']['total_chunks']} chunks processados")

if __name__ == '__main__':
    # Verificar se deve testar OpenAI ou scraper normal
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--openai':
            test_openai_integration()
        elif sys.argv[1] == '--rag':
            test_full_rag_integration()
        elif sys.argv[1] == '--help':
            print("Uso:")
            print("  python scraper.py           # Teste básico do scraper")
            print("  python scraper.py --openai  # Teste chunking + embeddings")
            print("  python scraper.py --rag     # Teste integração completa RAG")
        else:
            test_scraper()
    else:
        test_scraper() 