import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class ConfiguracaoBanco:

    servidor: str
    banco: str
    driver: str
    trusted_connection: str
    encrypt: str
    trust_server_certificate: str


def _obter_variavel_obrigatoria(nome: str) -> str:

    valor = os.getenv(nome)

    if valor is None or not valor.strip():
        raise RuntimeError(f"A variável de ambiente {nome} não foi configurada.")

    return valor.strip()


def carregar_configuracao_banco() -> ConfiguracaoBanco:

    load_dotenv()

    return ConfiguracaoBanco(
        servidor=_obter_variavel_obrigatoria("SQL_SERVER"),
        banco=_obter_variavel_obrigatoria("SQL_DATABASE"),
        driver=_obter_variavel_obrigatoria("SQL_DRIVER" ),
        trusted_connection=_obter_variavel_obrigatoria("SQL_TRUSTED_CONNECTION"),
        encrypt=_obter_variavel_obrigatoria("SQL_ENCRYPT"),
        trust_server_certificate=( _obter_variavel_obrigatoria("SQL_TRUST_SERVER_CERTIFICATE"))
    )