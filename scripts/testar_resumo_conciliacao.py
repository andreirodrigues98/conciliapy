from decimal import Decimal

from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.models.resumo_conciliacao import ResumoConciliacao



resumo = ResumoConciliacao(
    quantidade_grupos=10,
    quantidade_conciliados=7,
    total_previsto=Decimal("1000.00"),
    total_pago=Decimal("900.00"),
    percentual_conciliado=Decimal("70.00"),
    contagem_por_status={
        StatusConciliacao.CONCILIADO: 7,
        StatusConciliacao.PAGAMENTO_PARCIAL: 3,
    },
)

print(resumo.quantidade_nao_conciliados)
print(resumo.diferenca_total)