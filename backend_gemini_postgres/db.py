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
