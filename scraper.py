import asyncio
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_url_content(url: str) -> dict:
    """
    Acessa uma URL usando o Playwright, extrai o título e o conteúdo de texto limpo.
    
    Args:
        url: A URL da página a ser capturada.

    Returns:
        Um dicionário contendo 'title' e 'content' da página, ou um dicionário de erro.
    """
    logger.info(f"Iniciando a captura da URL: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            await page.goto(url, timeout=60000, wait_until='domcontentloaded')
            
            html_content = await page.content()
            title = await page.title()
            
            await browser.close()

            soup = BeautifulSoup(html_content, 'html.parser')
            
            for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
                script_or_style.decompose()

            body_text = soup.body.get_text(separator='\\n', strip=True)

            logger.info(f"Captura da URL '{url}' concluída. Título: '{title}'")
            return {
                "success": True,
                "title": title,
                "content": body_text
            }
            
    except Exception as e:
        logger.error(f"Ocorreu um erro ao capturar a URL {url}: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao processar a URL: {e}"
        }

def scrape_url(url: str) -> dict:
    """Função síncrona que envolve a função assíncrona scrape_url_content."""
    return asyncio.run(scrape_url_content(url))

if __name__ == '__main__':
    # Exemplo de uso para teste:
    # python scraper.py
    test_url = 'https://www.gov.br/pgr/pt-br'
    print(f"Testando captura da URL: {test_url}")
    result = scrape_url(test_url)
    if result['success']:
        print(f"\\nTítulo: {result['title']}")
        print(f"\\nConteúdo (primeiros 500 caracteres):\\n{result['content'][:500]}...")
    else:
        print(f"\\nErro na captura: {result['error']}") 