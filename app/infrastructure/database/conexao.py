from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.config import ConfiguracaoBanco, carregar_configuracao_banco


def criar_url_conexao(configuracao: ConfiguracaoBanco) -> URL:

    string_odbc = (
        f"DRIVER={{{configuracao.driver}}};"
        f"SERVER={configuracao.servidor};"
        f"DATABASE={configuracao.banco};"
        f"Trusted_Connection="
        f"{configuracao.trusted_connection};"
        f"Encrypt={configuracao.encrypt};"
        f"TrustServerCertificate="
        f"{configuracao.trust_server_certificate};"
    )

    return URL.create("mssql+pyodbc",query={"odbc_connect": string_odbc})


def criar_engine(configuracao: ConfiguracaoBanco | None = None) -> Engine:

    if configuracao is None:
        configuracao = carregar_configuracao_banco()

    url_conexao = criar_url_conexao(configuracao=configuracao)

    return create_engine(url_conexao, pool_pre_ping=True)


def criar_fabrica_sessoes(engine: Engine) -> sessionmaker[Session]:

    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)