from dataclasses import dataclass
from decimal import Decimal

from app.domain.enums.status_conciliacao import StatusConciliacao
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

        self.mensagem = self.mensagem.strip()

        if not self.mensagem:
            raise ValueError("A mensagem não pode estar vazia.")

    @property
    def total_previsto(self) -> Decimal:
        return self.grupo.total_previsto

    @property 
    def total_pago(self) -> Decimal:
        return self.grupo.total_pago

    @property 
    def diferenca(self) -> Decimal:
        return self.grupo.diferenca









