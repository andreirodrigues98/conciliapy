from decimal import Decimal
from dataclasses import dataclass

from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.models.resultado_conciliacao import ResultadoConciliacao
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.grupo_conciliacao import GrupoConciliacao

@dataclass

class ResultadoGrupoConciliacao:

    grupo: GrupoConciliacao
    status: StatusConciliacao
    mensagem: str

    def __post_init__(self) -> None:

        if not isinstance(self.grupo, GrupoConciliacao):
            raise TypeError("O grupo deve ser uma instância de GrupoConciliacao.")

        if not isinstance(self.status, StatusConciliacao):
            raise TypeError("O status  deve ser uma instância de StatusConciliacao.")

        if not isinstance(self.mensagem, str):
            raise TypeError("A mensagem deve ser uma string.")

    @property
    def total_previsto(self):
        return self.grupo.total_previsto

    @property 
    def total_pago(self):
        return self.grupo.total_pago

    @property 
    def diferenca(self):
        return self.grupo.diferenca









