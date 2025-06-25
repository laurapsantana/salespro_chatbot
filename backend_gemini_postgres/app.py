from flask_cors import CORS
from flask import Flask, request, jsonify
from db import conectar
import google.generativeai as genai
import traceback


app = Flask(__name__)
CORS(app)

genai.configure(api_key="AIzaSyAelq7EUC3n_bwe1FMZpRiD-lKDuaFbYM4")  # Substitua pela sua chave real

def extrair_mes(pergunta):
    meses = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
        "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
    }
    for nome, numero in meses.items():
        if nome in pergunta:
            return numero
    return None

def interpretar_pergunta(pergunta):
    pergunta = pergunta.lower()
    mes = extrair_mes(pergunta)

    if "mês" in pergunta and "vendas" in pergunta:
        return f"""
            SELECT 
                TO_CHAR(data_emissao, 'YYYY-MM') AS mes,
                SUM(total) AS total
            FROM public.fatec_vendas
            GROUP BY TO_CHAR(data_emissao, 'YYYY-MM')
            ORDER BY total DESC
            LIMIT 1;
        """

    elif mes and "cliente" in pergunta and ("mais" in pergunta or "comprou" in pergunta):
        return f"""
            SELECT razao_cliente, SUM(total) AS total_compras
            FROM public.fatec_vendas
            WHERE EXTRACT(MONTH FROM data_emissao) = {mes}
            GROUP BY razao_cliente
            ORDER BY total_compras DESC
            LIMIT 10;
        """

    elif mes and "cliente" in pergunta and ("menos" in pergunta or "pouco" in pergunta):
        return f"""
            SELECT razao_cliente, SUM(total) AS total_compras
            FROM public.fatec_vendas
            WHERE EXTRACT(MONTH FROM data_emissao) = {mes}
            GROUP BY razao_cliente
            ORDER BY total_compras ASC
            LIMIT 10;
        """

    elif mes and "produto" in pergunta:
        return f"""
            SELECT descricao_produto, SUM(qtde) AS total_vendido
            FROM public.fatec_vendas
            WHERE EXTRACT(MONTH FROM data_emissao) = {mes}
            GROUP BY descricao_produto
            ORDER BY total_vendido DESC
            LIMIT 10;
        """

    elif "produto" in pergunta and ("quantidade" in pergunta or "vendido" in pergunta):
        return """
            SELECT descricao_produto, SUM(qtde) AS total_vendido
            FROM public.fatec_vendas
            GROUP BY descricao_produto
            ORDER BY total_vendido DESC
            LIMIT 10;
        """

    elif "produto" in pergunta and ("menos vendido" in pergunta or "vendeu pouco" in pergunta):
        return """
            SELECT descricao_produto, SUM(qtde) AS total_vendido
            FROM public.fatec_vendas
            GROUP BY descricao_produto
            ORDER BY total_vendido ASC
            LIMIT 10;
        """

    elif "cliente" in pergunta and ("menos comprou" in pergunta or "menos compras" in pergunta):
        return """
            SELECT razao_cliente, SUM(total) AS total_compras
            FROM public.fatec_vendas
            GROUP BY razao_cliente
            ORDER BY total_compras ASC
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

    elif "cidade" in pergunta and ("mais vendeu" in pergunta or "desempenho" in pergunta):
        return """
            SELECT cidade, uf, SUM(total) AS total_vendas
            FROM public.fatec_vendas
            GROUP BY cidade, uf
            ORDER BY total_vendas DESC
            LIMIT 5;
        """

    elif "clientes frequentes" in pergunta or ("clientes" in pergunta and "mês" in pergunta):
        return """
            SELECT 
                id_cliente,
                razao_cliente,
                SUM(total) AS total_compras
            FROM 
                public.fatec_vendas 
            WHERE 
                EXTRACT(YEAR FROM data_emissao) = 2024
            GROUP BY 
                id_cliente, razao_cliente
            ORDER BY 
                total_compras DESC
            LIMIT 10;
        """

    elif "produtos com maior ticket médio" in pergunta:
        return """
            SELECT descricao_produto, SUM(total)/SUM(qtde) AS ticket_medio
            FROM public.fatec_vendas
            GROUP BY descricao_produto
            HAVING SUM(qtde) > 0
            ORDER BY ticket_medio DESC
            LIMIT 10;
        """

    elif "ticket médio" in pergunta and "cliente" in pergunta:
        return """
            SELECT razao_cliente, SUM(total)/COUNT(DISTINCT id_nf) AS ticket_medio
            FROM public.fatec_vendas
            GROUP BY razao_cliente
            ORDER BY ticket_medio DESC
            LIMIT 10;
        """

    else:
        return """
            SELECT descricao_produto, qtde, total
            FROM public.fatec_vendas
            LIMIT 5;
        """

def formatar_dados_para_texto(dados, colunas=None):
    texto = ""
    if colunas:
        texto += " | ".join(colunas) + "\n"
        texto += "-" * 50 + "\n"
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
        colunas = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()

        dados_formatados = formatar_dados_para_texto(resultado, colunas)

        prompt = (
            "Você é um assistente inteligente que responde perguntas com base nos dados a seguir:\n"
            f"{dados_formatados}\n"
            f"Pergunta do usuário: {pergunta}\n"
            "Por favor, gere um relatório detalhado, organizado e visualmente atrativo usando emojis e destaques.\n"
            "Ao final, informe que o usuário pode fazer perguntas como:\n"
            "- Qual mês teve mais vendas?\n"
            "- Quem mais comprou em julho?\n"
            "- Produtos que menos venderam em março\n"
            "- Qual cidade mais vendeu?\n"
            "- Clientes frequentes\n"
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        resposta = model.generate_content(prompt)

        return jsonify({"relatorio": resposta.text})

    except Exception:
        print(traceback.format_exc())
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
