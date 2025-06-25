import psycopg2

def conectar():
    try:
        conn = psycopg2.connect(
            host="salesprodb-laura.postgres.database.azure.com",
            database="sales_pro",
            user="acesso_rad",  # use o usuário completo
            password="SenhaForte123",
            port="5432",
            sslmode="require"
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco:", e)
        return None

def testar_conexao():
    conn = conectar()
    if conn is None:
        print("Falha ao conectar ao banco.")
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")  # Consulta simples para testar
        resultado = cursor.fetchone()
        print("Conexão OK! Hora do servidor:", resultado[0])
        cursor.close()
    except Exception as e:
        print("Erro durante a consulta:", e)
    finally:
        conn.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    testar_conexao()