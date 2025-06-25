import google.generativeai as genai

def testar_gemini():
    genai.configure(api_key="AIzaSyAelq7EUC3n_bwe1FMZpRiD-lKDuaFbYM4")
    model = genai.GenerativeModel("text-bison-001")

    # Exemplo usando o parâmetro 'messages' para chat
    resposta = model.generate_content(
        messages=[
            {"role": "user", "content": "Me diga uma frase inspiradora."}
        ]
    )
    print(resposta.candidates[0].content)

if __name__ == "__main__":
    testar_gemini()
