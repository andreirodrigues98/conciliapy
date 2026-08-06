from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import (
    ConfiguracaoConciliacao,
)
from app.infrastructure.readers.leitor_planilha_excel import (
    COLUNA_LINHA_ORIGEM,
)
from app.infrastructure.transformers.conversor_dataframe_registros import (
    ConversorDataFrameRegistros,
)


def criar_configuracao() -> ConfiguracaoConciliacao:
    return ConfiguracaoConciliacao(
        nome="Configuração de teste",
        tipo_entrada=TipoEntrada.DUAS_PLANILHAS,
        chave_conciliacao=("identificador",),
        tolerancia=Decimal("0.05"),
        mapeamento_vendas={
            "identificador": "ID Venda",
            "cliente": "Comprador",
            "data": "Data Venda",
            "valor_previsto": "Total Pedido",
        },
        mapeamento_pagamentos={
            "identificador": "ID Venda",
            "cliente": "Comprador",
            "data": "Data Pagamento",
            "valor_pago": "Valor Recebido",
        },
    )


def test_converter_previsoes_cria_registro_financeiro() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "ID Venda": "PED-101",
                "Comprador": "Ana Silva",
                "Data Venda": "05/01/2026",
                "Total Pedido": 500,
                COLUNA_LINHA_ORIGEM: 2,
            }
        ]
    )

    conversor = ConversorDataFrameRegistros()

    registros = conversor.converter_previsoes(
        dataframe=dataframe,
        configuracao=criar_configuracao(),
        arquivo_origem="vendas.xlsx",
        aba_origem="Vendas",
    )

    assert len(registros) == 1

    registro = registros[0]

    assert registro.identificador == "PED-101"
    assert registro.cliente == "Ana Silva"
    assert registro.data == date(2026, 1, 5)
    assert registro.valor_previsto == Decimal("500.00")
    assert registro.valor_pago == Decimal("0.00")
    assert registro.linha_origem == 2


def test_converter_pagamentos_aceita_valor_brasileiro() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "ID Venda": "PED-101",
                "Comprador": "Ana Silva",
                "Data Pagamento": "10/01/2026",
                "Valor Recebido": "R$ 1.234,56",
                COLUNA_LINHA_ORIGEM: 3,
            }
        ]
    )

    conversor = ConversorDataFrameRegistros()

    registros = conversor.converter_pagamentos(
        dataframe=dataframe,
        configuracao=criar_configuracao(),
        arquivo_origem="pagamentos.xlsx",
        aba_origem="Pagamentos",
    )

    registro = registros[0]

    assert registro.valor_previsto == Decimal("0.00")
    assert registro.valor_pago == Decimal("1234.56")
    assert registro.data == date(2026, 1, 10)
    assert registro.linha_origem == 3


def test_converter_previsoes_rejeita_coluna_ausente() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "ID Venda": "PED-101",
                "Comprador": "Ana Silva",
                "Data Venda": "05/01/2026",
            }
        ]
    )

    conversor = ConversorDataFrameRegistros()

    with pytest.raises(
        ValueError,
        match="Total Pedido",
    ):
        conversor.converter_previsoes(
            dataframe=dataframe,
            configuracao=criar_configuracao(),
            arquivo_origem="vendas.xlsx",
            aba_origem="Vendas",
        )