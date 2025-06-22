// background.js - Service Worker para Manifest V3

// Service worker básico - apenas mantém a extensão ativa
self.addEventListener('install', () => {
  console.log('RAG-Control Service Worker instalado');
});

self.addEventListener('activate', () => {
  console.log('RAG-Control Service Worker ativado');
});

// Criar menu de contexto quando a extensão for instalada
chrome.runtime.onInstalled.addListener(() => {
  try {
    chrome.contextMenus.create({
      id: 'open-rag-popup',
      title: 'Salvar Página no Agente RAG',
      contexts: ['page']
    });
  } catch (error) {
    console.log('Menu de contexto já existe ou erro:', error);
  }
});

// Handler para cliques no menu de contexto
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'open-rag-popup') {
    // Abrir popup programaticamente
    chrome.action.openPopup().catch(() => {
      // Se falhar, tentar abrir a aba de opções
      chrome.tabs.create({ url: chrome.runtime.getURL('popup.html') });
    });
  }
}); 