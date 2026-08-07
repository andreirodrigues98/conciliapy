from decimal import Decimal
from pathlib import Path

import pandas as pd

from app.application.models.resultado_execucao_conciliacao import ResultadoExecucaoConciliacao
from app.application.services.servico_conciliacao_planilhas import ServicoConciliacaoPlanilhas
from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import  ConfiguracaoConciliacao
from app.domain.services.calculador_resumo_conciliacao import CalculadorResumoConciliacao
from app.infrastructure.readers.leitor_planilha_excel import LeitorPlanilhaExcel
from app.infrastructure.transformers.conversor_dataframe_registros import ConversorDataFrameRegistros
from app.infrastructure.transformers.conversor_resultados_dataframe import ConversorResultadosDataFrame


def test_executar_conciliacao_do_inicio_ao_fim(
    tmp_path: Path,
) -> None:
    caminho_vendas = tmp_path / "vendas.xlsx"
    caminho_pagamentos = tmp_path / "pagamentos.xlsx"

    dataframe_vendas = pd.DataFrame(
        [
            {
                "Identificador": "PED-101",
                "Cliente": "Ana Silva",
                "Data": "05/01/2026",
                "Valor Previsto": 300.00,
            },
            {
                "Identificador": "PED-102",
                "Cliente": "Carlos Souza",
                "Data": "06/01/2026",
                "Valor Previsto": 200.00,
            },
        ]
    )

    dataframe_pagamentos = pd.DataFrame(
        [
            {
                "ID Venda": "PED-101",
                "Comprador": "Ana Silva",
                "Data Pagamento": "10/01/2026",
                "Valor Recebido": 100.00,
            },
            {
                "ID Venda": "PED-101",
                "Comprador": "Ana Silva",
                "Data Pagamento": "15/01/2026",
                "Valor Recebido": 200.00,
            },
            {
                "ID Venda": "PED-103",
                "Comprador": "Marina Lima",
                "Data Pagamento": "20/01/2026",
                "Valor Recebido": 500.00,
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
        calculador_resumo=CalculadorResumoConciliacao(),
        conversor_resultados=ConversorResultadosDataFrame(),
    )

    execucao = servico.executar(
        configuracao=configuracao,
        caminho_vendas=caminho_vendas,
        caminho_pagamentos=caminho_pagamentos,
        aba_vendas="Vendas",
        aba_pagamentos="Pagamentos",
    )

    assert isinstance(
        execucao,
        ResultadoExecucaoConciliacao,
    )

    assert len(execucao.resultados) == 3

    resultados_por_chave = {
        resultado.grupo.chave: resultado
        for resultado in execucao.resultados
    }

    assert (resultados_por_chave[("PED-101",)].status == StatusConciliacao.CONCILIADO)

    assert (resultados_por_chave[("PED-102",)].status== StatusConciliacao.VENDA_SEM_PAGAMENTO)

    assert (resultados_por_chave[("PED-103",)].status == StatusConciliacao.PAGAMENTO_SEM_VENDA)

    assert execucao.resumo.quantidade_grupos == 3

    assert (execucao.resumo.quantidade_conciliados == 1)

    assert (execucao.resumo.quantidade_nao_conciliados == 2)

    assert (execucao.resumo.total_previsto == Decimal("500.00"))

    assert (execucao.resumo.total_pago == Decimal("800.00"))

    assert (execucao.resumo.diferenca_total== Decimal("300.00"))

    assert (execucao.resumo.percentual_conciliado == Decimal("33.33"))

    assert (execucao.resumo.contagem_por_status[StatusConciliacao.CONCILIADO] == 1)

    assert not execucao.dataframe_resultados.empty

    assert ("Status" in execucao.dataframe_resultados.columns)

    assert (len(execucao.dataframe_resultados) == len(execucao.resultados))