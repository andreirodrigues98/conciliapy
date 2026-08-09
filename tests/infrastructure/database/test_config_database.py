import pytest

from app.infrastructure.database.config import carregar_configuracao_banco


def test_carregar_configuracao_banco(monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.setenv("SQL_SERVER",  r".\SQLEXPRESS")
    monkeypatch.setenv("SQL_DATABASE", "ConciliaPy")
    monkeypatch.setenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
    monkeypatch.setenv("SQL_TRUSTED_CONNECTION", "yes")
    monkeypatch.setenv("SQL_ENCRYPT", "yes")
    monkeypatch.setenv("SQL_TRUST_SERVER_CERTIFICATE", "yes")

    configuracao = carregar_configuracao_banco()

    assert configuracao.servidor == r".\SQLEXPRESS"
    assert configuracao.banco == "ConciliaPy"
    assert configuracao.driver == "ODBC Driver 18 for SQL Server"
    assert configuracao.trusted_connection == "yes"
    assert configuracao.encrypt == "yes"
    assert configuracao.trust_server_certificate == "yes"


def test_carregar_configuracao_rejeita_variavel_ausente(monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.setenv("SQL_SERVER", r".\SQLEXPRESS")
    monkeypatch.setenv("SQL_DATABASE", "")

    monkeypatch.setenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server" )
    monkeypatch.setenv("SQL_TRUSTED_CONNECTION", "yes")
    monkeypatch.setenv("SQL_ENCRYPT", "yes")
    monkeypatch.setenv("SQL_TRUST_SERVER_CERTIFICATE", "yes")

    with pytest.raises(RuntimeError, match="SQL_DATABASE"):
        carregar_configuracao_banco()