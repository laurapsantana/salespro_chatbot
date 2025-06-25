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

    if "mês" in pergunta and "vendas" in pergunta:
        return """
            SELECT 
                TO_CHAR(data_emissao, 'YYYY-MM') AS mes,
                SUM(total) AS total
            FROM public.fatec_vendas
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT 6;
        """
    elif "produto" in pergunta and ("quantidade" in pergunta or "vendido" in pergunta):
        return """
            SELECT descricao_produto, SUM(qtde) AS total_vendido
            FROM public.fatec_vendas
            GROUP BY descricao_produto
            ORDER BY total_vendido DESC
            LIMIT 10;
        """
    elif "cliente" in pergunta and ("mais comprou" in pergunta or "frequente" in pergunta):
        return """
            SELECT razao_cliente, SUM(total) AS total_compras
            FROM public.fatec_vendas
            GROUP BY razao_cliente
            ORDER BY total_compras DESC
            LIMIT 10;
        """
    else:
        return """
            SELECT descricao_produto, preco_unitario, qtde
            FROM public.fatec_vendas
            LIMIT 5;
        """

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
            "🎯 Você é um assistente de dados de vendas da empresa SalesPro.\n\n"
            "📊 Abaixo estão os dados obtidos do banco:\n\n"
            f"{dados_formatados}\n\n"
            "🧠 Com base nesses dados, responda à seguinte pergunta do usuário:\n"
            f"❓ {pergunta}\n\n"
            "✅ Gere uma resposta clara, direta e organizada, usando emojis e quebras de linha quando possível.\n"
            "Destaque o resultado mais relevante e forneça observações se aplicável."
        )


        model = genai.GenerativeModel("gemini-1.5-flash")
        resposta = model.generate_content(prompt)

        return jsonify({"relatorio": resposta.text})

    except Exception:
        print(traceback.format_exc())
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
