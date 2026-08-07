from dataclasses import dataclass
from decimal import Decimal

from app.domain.enums.status_conciliacao import StatusConciliacao


@dataclass
class ResumoConciliacao:

    quantidade_grupos: int
    quantidade_conciliados: int 
    total_previsto: Decimal
    total_pago: Decimal
    percentual_conciliado: Decimal
    contagem_por_status: dict[StatusConciliacao, int]

    @property
    def quantidade_nao_conciliados(self) -> int:
        return self.quantidade_grupos - self.quantidade_conciliados

    @property
    def diferenca_total(self) -> Decimal:
        return self.total_pago - self.total_previsto
    



