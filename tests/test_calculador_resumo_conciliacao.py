from datetime import date
from decimal import Decimal

import pytest

from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.models.grupo_conciliacao import GrupoConciliacao
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao
from app.domain.services.calculador_resumo_conciliacao import CalculadorResumoConciliacao


def criar_resultado(identificador: str, valor_previsto: str, valor_pago: str, status: StatusConciliacao,):

    previsao = RegistroFinanceiro(
        identificador=identificador,
        cliente="Cliente Teste",
        data=date(2026, 1, 1),
        valor_previsto=Decimal(valor_previsto),
        valor_pago=Decimal("0.00"),
        arquivo_origem="vendas.xlsx",
        aba_origem="Vendas",
        linha_origem=2,
    )

    pagamento = RegistroFinanceiro(
        identificador=identificador,
        cliente="Cliente Teste",
        data=date(2026, 1, 2),
        valor_previsto=Decimal("0.00"),
        valor_pago=Decimal(valor_pago),
        arquivo_origem="pagamentos.xlsx",
        aba_origem="Pagamentos",
        linha_origem=2,
    )

    grupo = GrupoConciliacao(
        chave=(identificador,),
        previsoes=[previsao],
        pagamentos=[pagamento],
    )

    return ResultadoGrupoConciliacao(
        grupo=grupo,
        status=status,
        mensagem="Resultado criado para teste.",
    )


def test_calcular_resumo_consolida_resultados() -> None:
    resultados = [
        criar_resultado(
            identificador="PED-101",
            valor_previsto="100.00",
            valor_pago="100.00",
            status=StatusConciliacao.CONCILIADO,
        ),
        criar_resultado(
            identificador="PED-102",
            valor_previsto="100.00",
            valor_pago="99.98",
            status=(
                StatusConciliacao.CONCILIADO_COM_TOLERANCIA
            ),
        ),
        criar_resultado(
            identificador="PED-103",
            valor_previsto="200.00",
            valor_pago="150.00",
            status=StatusConciliacao.PAGAMENTO_PARCIAL,
        ),
    ]

    calculador = CalculadorResumoConciliacao()

    resumo = calculador.calcular(
        resultados=resultados
    )

    assert resumo.quantidade_grupos == 3
    assert resumo.quantidade_conciliados == 2
    assert resumo.quantidade_nao_conciliados == 1
    
    assert resumo.total_pago == Decimal("349.98")
    assert resumo.total_previsto == Decimal("400.00")
    assert resumo.diferenca_total == Decimal("-50.02")
    assert resumo.percentual_conciliado == Decimal("66.67")

    assert resumo.contagem_por_status[StatusConciliacao.CONCILIADO]  == 1
    assert resumo.contagem_por_status[StatusConciliacao.CONCILIADO_COM_TOLERANCIA]  == 1
    assert resumo.contagem_por_status[StatusConciliacao.PAGAMENTO_PARCIAL]  == 1

def test_calcular_lista_vazia_retorna_resumo_zerado() -> None:

    calculador = CalculadorResumoConciliacao()

    resumo = calculador.calcular(resultados=[])

    assert resumo.quantidade_grupos == 0
    assert resumo.quantidade_nao_conciliados == 0
    assert resumo.quantidade_conciliados == 0

    assert resumo.total_pago == Decimal("0.00")
    assert resumo.total_previsto == Decimal("0.00")
    assert resumo.diferenca_total == Decimal("0.00")
    assert resumo.percentual_conciliado == Decimal("0.00")

def test_calcular_rejeita_resultado_invalido() -> None:

    calculador = CalculadorResumoConciliacao()

    with pytest.raises(TypeError, match="posição 0"):
        calculador.calcular(resultados=["resultado Inválido"])
