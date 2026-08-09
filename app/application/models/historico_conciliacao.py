from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ItemHistoricoConciliacao:

    id: int
    nome: str
    tipo_entrada: str
    data_execucao: datetime

    quantidade_grupos: int
    quantidade_conciliados: int

    total_previsto: Decimal
    total_pago: Decimal
    diferenca_total: Decimal
    percentual_conciliado: Decimal

    @property
    def quantidade_nao_conciliados(self) -> int:

        return (self.quantidade_grupos - self.quantidade_conciliados)


@dataclass(frozen=True)
class ResultadoHistoricoConciliacao:

    chave: str
    status: str

    total_previsto: Decimal
    total_pago: Decimal
    diferenca: Decimal

    quantidade_previsoes: int
    quantidade_pagamentos: int

    mensagem: str


@dataclass(frozen=True)
class DetalheHistoricoConciliacao(ItemHistoricoConciliacao):

    tolerancia: Decimal

    arquivo_vendas: str
    arquivo_pagamentos: str

    resultados: tuple[ ResultadoHistoricoConciliacao, ...]