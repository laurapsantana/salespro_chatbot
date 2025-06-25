import google.generativeai as genai

# Configure sua API key certa aqui
genai.configure(api_key="AIzaSyAelq7EUC3n_bwe1FMZpRiD-lKDuaFbYM4")

def analisar_tendencias(dados):
    if not dados:
        return "Não há dados suficientes para análise."

    prompt = "Analise as tendências de vendas com base nos dados abaixo:\n"
    for nome, total in dados:
        prompt += f"- Produto: {nome}, Total vendido: {total}\n"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # Modelo oficial do Gemini para texto
        resposta = model.generate(prompt=prompt)
        return resposta.text
    except Exception as e:
        print("Erro com a API do Gemini:", e)
        return "Não foi possível analisar as tendências no momento."
