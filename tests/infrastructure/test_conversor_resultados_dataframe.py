from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.models.grupo_conciliacao import  GrupoConciliacao
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao
from app.infrastructure.transformers.conversor_resultados_dataframe import COLUNAS_RESULTADO, ConversorResultadosDataFrame


def test_converter_cria_dataframe_com_resultado() -> None:
    previsao = RegistroFinanceiro(
        identificador="PED-101",
        cliente="Ana Silva",
        data=date(2026, 1, 5),
        valor_previsto=Decimal("300.00"),
        valor_pago=Decimal("0.00"),
        arquivo_origem="vendas.xlsx",
        aba_origem="Vendas",
        linha_origem=2,
    )

    pagamento = RegistroFinanceiro(
        identificador="PED-101",
        cliente="Ana Silva",
        data=date(2026, 1, 10),
        valor_previsto=Decimal("0.00"),
        valor_pago=Decimal("300.00"),
        arquivo_origem="pagamentos.xlsx",
        aba_origem="Pagamentos",
        linha_origem=2,
    )

    grupo = GrupoConciliacao(
        chave=("PED-101",),
        previsoes=[previsao],
        pagamentos=[pagamento],
    )

    resultado = ResultadoGrupoConciliacao(
        grupo=grupo,
        status=StatusConciliacao.CONCILIADO,
        mensagem="Os valores foram conciliados.",
    )

    conversor = ConversorResultadosDataFrame()

    dataframe = conversor.converter(
        resultados=[resultado]
    )

    assert isinstance(dataframe, pd.DataFrame)

    assert list(dataframe.columns) == list(
        COLUNAS_RESULTADO
    )

    assert dataframe.loc[0, "Chave"] == "PED-101"

    assert (
        dataframe.loc[0, "Status"]
        == StatusConciliacao.CONCILIADO.value
    )

    assert dataframe.loc[0, "Total Previsto"] == 300.0
    assert dataframe.loc[0, "Total Pago"] == 300.0
    assert dataframe.loc[0, "Diferença"] == 0.0

    assert (
        dataframe.loc[0, "Quantidade de Previsões"]
        == 1
    )

    assert (
        dataframe.loc[0, "Quantidade de Pagamentos"]
        == 1
    )

def test_converter_rejeita_item_invalido() -> None:
    conversor = ConversorResultadosDataFrame()

    with pytest.raises(TypeError, match="posição 0"):
        conversor.converter(
            resultados=["resultado inválido"]  
        )

def test_converter_lista_vazia_cria_dataframe_vazio() -> None:

    conversor = ConversorResultadosDataFrame() 

    dataframe = conversor.converter(resultados=[])

    assert dataframe.empty
    assert list(dataframe.columns) == list(COLUNAS_RESULTADO)