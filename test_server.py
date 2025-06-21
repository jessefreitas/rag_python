"""
Servidor de teste simples para verificar se o Flask está funcionando
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste - Sistema RAG</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Sistema Web de Agentes RAG</h1>
            <p>Servidor funcionando corretamente!</p>
            
            <div class="card">
                <h3>Status do Sistema</h3>
                <p>✅ Servidor Flask rodando</p>
                <p>✅ Templates funcionando</p>
                <p>✅ Rotas configuradas</p>
            </div>
            
            <div class="card">
                <h3>Próximos Passos</h3>
                <p>1. Verificar se as dependências estão instaladas</p>
                <p>2. Configurar o sistema completo</p>
                <p>3. Testar criação de agentes</p>
            </div>
            
            <a href="/test" class="btn">Testar Rota</a>
        </div>
    </body>
    </html>
    """)

@app.route('/test')
def test():
    return "✅ Rota de teste funcionando!"

@app.route('/api/test')
def api_test():
    return {"status": "success", "message": "API funcionando!"}

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste...")
    print("📡 Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 