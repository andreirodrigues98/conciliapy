from decimal import Decimal
from pathlib import Path

from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import (
    ConfiguracaoConciliacao,
)
from app.infrastructure.readers.leitor_planilha_excel import (
    LeitorPlanilhaExcel,
)
from app.infrastructure.transformers.conversor_dataframe_registros import (
    ConversorDataFrameRegistros,
)


def executar() -> None:
    """Lê as planilhas e converte suas linhas em registros."""

    configuracao = ConfiguracaoConciliacao(
        nome="Conciliação por pedido",
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

    caminho_vendas = (
        Path("data")
        / "entrada"
        / "vendas.xlsx"
    )

    caminho_pagamentos = (
        Path("data")
        / "entrada"
        / "pagamentos.xlsx"
    )

    leitor = LeitorPlanilhaExcel()
    conversor = ConversorDataFrameRegistros()

    dataframe_vendas = leitor.ler(
    caminho_arquivo=caminho_vendas,
    aba=0,
    )

    

    dataframe_pagamentos = leitor.ler(
        caminho_arquivo=caminho_pagamentos,
        aba=0,
    )

    previsoes = conversor.converter_previsoes(
        dataframe=dataframe_vendas,
        configuracao=configuracao,
        arquivo_origem=caminho_vendas,
        aba_origem="Vendas",
    )

    pagamentos = conversor.converter_pagamentos(
        dataframe=dataframe_pagamentos,
        configuracao=configuracao,
        arquivo_origem=caminho_pagamentos,
        aba_origem="Pagamentos",
    )

    print("\nPrevisões convertidas:")

    for registro in previsoes:
        print(
            registro.identificador,
            registro.cliente,
            registro.valor_previsto,
            registro.linha_origem,
        )

    print("\nPagamentos convertidos:")

    for registro in pagamentos:
        print(
            registro.identificador,
            registro.cliente,
            registro.valor_pago,
            registro.linha_origem,
        )


if __name__ == "__main__":
    executar()