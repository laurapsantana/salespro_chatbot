import google.generativeai as genai
from dotenv import load_dotenv
import os

# Carrega variáveis do .env (caso esteja usando)
load_dotenv()

def testar_gemini():
    # Pega a chave da variável de ambiente
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")

    resposta = model.generate_content("Me diga uma frase inspiradora.")
    print(resposta.text)

if __name__ == "__main__":
    testar_gemini()
