from unittest.mock import MagicMock

from app.infrastructure.database.config import ConfiguracaoBanco
from app.infrastructure.database import conexao as modulo_conexao


def criar_configuracao_teste() -> ConfiguracaoBanco:

    return ConfiguracaoBanco(
        servidor=r".\SQLEXPRESS",
        banco="ConciliaPy",
        driver="ODBC Driver 18 for SQL Server",
        trusted_connection="yes",
        encrypt="yes",
        trust_server_certificate="yes",
    )


def test_criar_url_conexao_monta_odbc_corretamente() -> None:

    configuracao = criar_configuracao_teste()

    url = modulo_conexao.criar_url_conexao(configuracao)

    assert url.drivername == "mssql+pyodbc"

    string_odbc = url.query["odbc_connect"]

    assert "DRIVER={ODBC Driver 18 for SQL Server};" in string_odbc
    assert r"SERVER=.\SQLEXPRESS;"  in string_odbc

    assert "DATABASE=ConciliaPy;" in string_odbc
    assert "Trusted_Connection=yes;" in string_odbc
    assert "Encrypt=yes;" in string_odbc
    assert "TrustServerCertificate=yes;" in string_odbc



def test_criar_engine_usa_url_e_pool_pre_ping(monkeypatch) -> None:

    engine_falso = object()

    create_engine_mock = MagicMock(return_value=engine_falso)

    monkeypatch.setattr(modulo_conexao, "create_engine",create_engine_mock)


    configuracao = criar_configuracao_teste()

    resultado = modulo_conexao.criar_engine(configuracao)

    assert resultado is engine_falso

    url_passada = (create_engine_mock.call_args.args[0])

    assert url_passada.drivername == "mssql+pyodbc"

    assert create_engine_mock.call_args.kwargs["pool_pre_ping"] is True
    