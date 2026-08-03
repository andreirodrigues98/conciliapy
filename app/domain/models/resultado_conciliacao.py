from dataclasses import dataclass
from decimal import Decimal

from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.enums.status_conciliacao import StatusConciliacao

@dataclass
class ResultadoConciliacao():

    registro: RegistroFinanceiro
    status: StatusConciliacao
    mensagem: str | None = None

    def __post_init__(self) -> None:

        if not isinstance(self.registro, RegistroFinanceiro):
            raise TypeError("O registro precisa ser uma instância do RegistroFinanceiro.")

        if not isinstance(self.status, StatusConciliacao):
            raise TypeError("O status precisa ser uma instância de StatusConciliacao.")

        if self.mensagem is not None:
            if not isinstance(self.mensagem, str):
                raise TypeError("A mensagem precisa ser uma string.")

            self.mensagem = self.mensagem.strip() or None

    @property
    def diferenca(self) -> Decimal:
        return self.registro.diferenca







