// background.js

// Este script tem como única função criar o menu de contexto
// para adicionar uma forma alternativa de acesso.
// A ação principal da extensão agora é controlada pelo popup.html,
// definido na chave "action" do manifest.json.

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'open-rag-popup',
    title: 'Salvar Página no Agente RAG',
    contexts: ['page'],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'open-rag-popup') {
    // Apenas abre o popup. Toda a lógica está no popup.js
    chrome.action.openPopup();
  }
}); 