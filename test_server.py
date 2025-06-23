"""
Servidor de teste simples para verificar se o Flask está funcionando
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "Servidor funcionando"})

@app.route('/api/agents')
def agents():
    return jsonify({
        "status": "success",
        "agents": [
            {"id": "geral", "name": "🤖 Agente Geral", "documents_count": 0},
            {"id": "juridico", "name": "⚖️ Agente Jurídico", "documents_count": 15}
        ]
    })

if __name__ == '__main__':
    print("🚀 Servidor teste na porta 5000")
    app.run(host='localhost', port=5000, debug=True) 