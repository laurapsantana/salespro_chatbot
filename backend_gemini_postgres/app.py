
from flask_cors import CORS
from flask import Flask, request, jsonify
from db import conectar
import google.generativeai as genai
import traceback

app = Flask(__name__)
CORS(app) 

genai.configure(api_key="AIzaSyAelq7EUC3n_bwe1FMZpRiD-lKDuaFbYM4")

def interpretar_pergunta(pergunta):
    pergunta = pergunta.lower()

    if "probabilidade" in pergunta or "tendência" in pergunta or "previsão" in pergunta:
        sql = """
            SELECT produto, AVG(vendas_mensais) AS media_vendas, STDDEV(vendas_mensais) AS desvio_vendas
            FROM vendas_historico
            GROUP BY produto
            ORDER BY media_vendas DESC
            LIMIT 10
        """
    elif "venda" in pergunta or "quantidade" in pergunta:
        sql = """
            SELECT descricao_produto, SUM(qtde) AS total_vendas
            FROM fatec_vendas
            GROUP BY descricao_produto
            ORDER BY total_vendas DESC
            LIMIT 10
        """
    elif "produto" in pergunta:
        sql = """
            SELECT id_produto, descricao_produto, preco, estoque
            FROM produtos
            LIMIT 10
        """
    else:
        # Consulta genérica, exibe os primeiros produtos
        sql = """
            SELECT id_produto, descricao_produto, preco, estoque
            FROM produtos
            LIMIT 5
        """
    return sql

def formatar_dados_para_texto(dados):
    texto = ""
    for linha in dados:
        texto += " | ".join(str(item) for item in linha) + "\n"
    return texto

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        dados = request.get_json(force=True)
        pergunta = dados.get("pergunta", "").strip()

        if not pergunta:
            return jsonify({"erro": "Envie uma pergunta no corpo da requisição"}), 400

        conn = conectar()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500

        sql = interpretar_pergunta(pergunta)
        cursor = conn.cursor()
        cursor.execute(sql)
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()

        dados_formatados = formatar_dados_para_texto(resultado)

        prompt = (
            "Você é um assistente inteligente que responde perguntas com base nos dados a seguir:\n"
            f"{dados_formatados}\n"
            f"Pergunta do usuário: {pergunta}\n"
            "Por favor, gere um relatório detalhado e claro em sua resposta."
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        resposta = model.generate_content(prompt)

        return jsonify({"relatorio": resposta.text})

    except Exception:
        print(traceback.format_exc())
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True)
