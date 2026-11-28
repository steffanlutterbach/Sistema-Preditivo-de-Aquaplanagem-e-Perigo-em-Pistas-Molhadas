
from database import testar_conexao

try:
    banco = testar_conexao()
    print(f"Conexão realizada com sucesso! Banco conectado: {banco}")

except Exception as erro:
    print("Erro ao conectar ao PostgreSQL:")
    print(erro)
