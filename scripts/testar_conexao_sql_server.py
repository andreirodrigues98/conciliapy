from sqlalchemy import text

from app.infrastructure.database.conexao import criar_engine


def executar() -> None:
    engine = criar_engine()

    with engine.connect() as conexao:
        resultado = conexao.execute(text("SELECT DB_NAME() AS BancoAtual"))

        banco_atual = resultado.scalar_one()

    print(f"Conexão realizada com sucesso: {banco_atual}")

if __name__ == "__main__":
    executar()