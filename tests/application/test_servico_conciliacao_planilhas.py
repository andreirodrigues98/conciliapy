from decimal import Decimal
from pathlib import Path

import pandas as pd

from app.application.services.servico_conciliacao_planilhas import ServicoConciliacaoPlanilhas
from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.infrastructure.readers.leitor_planilha_excel import LeitorPlanilhaExcel

from app.infrastructure.transformers.conversor_dataframe_registros import ConversorDataFrameRegistros


def test_executar_concilia_planilhas_do_inicio_ao_fim(tmp_path: Path) -> None:
    caminho_vendas = tmp_path / "vendas.xlsx"
    caminho_pagamentos = tmp_path / "pagamentos.xlsx"

    dataframe_vendas = pd.DataFrame(
        [
            {
                "Identificador": "PED-101",
                "Cliente": "Ana Silva",
                "Data": "05/01/2026",
                "Valor Previsto": 300,
            },
            {
                "Identificador": "PED-102",
                "Cliente": "Carlos Souza",
                "Data": "06/01/2026",
                "Valor Previsto": 200,
            },
        ]
    )

    dataframe_pagamentos = pd.DataFrame(
        [
            {
                "ID Venda": "PED-101",
                "Comprador": "Ana Silva",
                "Data Pagamento": "10/01/2026",
                "Valor Recebido": 100,
            },
            {
                "ID Venda": "PED-101",
                "Comprador": "Ana Silva",
                "Data Pagamento": "15/01/2026",
                "Valor Recebido": 200,
            },
            {
                "ID Venda": "PED-103",
                "Comprador": "Marina Lima",
                "Data Pagamento": "20/01/2026",
                "Valor Recebido": 500,
            },
        ]
    )

    dataframe_vendas.to_excel(
        caminho_vendas,
        index=False,
        sheet_name="Vendas",
    )

    dataframe_pagamentos.to_excel(
        caminho_pagamentos,
        index=False,
        sheet_name="Pagamentos",
    )

    configuracao = ConfiguracaoConciliacao(
        nome="Teste de integração",
        tipo_entrada=TipoEntrada.DUAS_PLANILHAS,
        chave_conciliacao=("identificador",),
        tolerancia=Decimal("0.05"),
        mapeamento_vendas={
            "identificador": "Identificador",
            "cliente": "Cliente",
            "data": "Data",
            "valor_previsto": "Valor Previsto",
        },
        mapeamento_pagamentos={
            "identificador": "ID Venda",
            "cliente": "Comprador",
            "data": "Data Pagamento",
            "valor_pago": "Valor Recebido",
        },
    )

    servico = ServicoConciliacaoPlanilhas(
        leitor=LeitorPlanilhaExcel(),
        conversor=ConversorDataFrameRegistros(),
    )

    resultados = servico.executar(
        configuracao=configuracao,
        caminho_vendas=caminho_vendas,
        caminho_pagamentos=caminho_pagamentos,
        aba_vendas="Vendas",
        aba_pagamentos="Pagamentos",
    )

    resultados_por_chave = {
        resultado.grupo.chave: resultado
        for resultado in resultados
    }

    assert (
        resultados_por_chave[("PED-101",)].status
        == StatusConciliacao.CONCILIADO
    )

    assert (
        resultados_por_chave[("PED-102",)].status
        == StatusConciliacao.VENDA_SEM_PAGAMENTO
    )

    assert (
        resultados_por_chave[("PED-103",)].status
        == StatusConciliacao.PAGAMENTO_SEM_VENDA
    )