from decimal import Decimal
from pathlib import Path

from app.application.services.servico_conciliacao_planilhas import (
    ServicoConciliacaoPlanilhas,
)
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


def criar_configuracao() -> ConfiguracaoConciliacao:

    return ConfiguracaoConciliacao(
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


def executar() -> None:

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

    servico = ServicoConciliacaoPlanilhas(
        leitor=LeitorPlanilhaExcel(),
        conversor=ConversorDataFrameRegistros(),
    )

    resultados = servico.executar(
        configuracao=criar_configuracao(),
        caminho_vendas=caminho_vendas,
        caminho_pagamentos=caminho_pagamentos,
        aba_vendas="Vendas",
        aba_pagamentos="Pagamentos"
    )

    for resultado in resultados:
        print("-" * 60)
        print(f"Chave: {resultado.grupo.chave}")
        print(f"Status: {resultado.status.value}")
        print(
            f"Total previsto: "
            f"R$ {resultado.total_previsto:.2f}"
        )
        print(
            f"Total pago: "
            f"R$ {resultado.total_pago:.2f}"
        )
        print(
            f"Diferença: "
            f"R$ {resultado.diferenca:.2f}"
        )
        print(f"Mensagem: {resultado.mensagem}")


if __name__ == "__main__":
    executar()