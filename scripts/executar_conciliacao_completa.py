from decimal import Decimal
from pathlib import Path

from app.application.services.servico_conciliacao_planilhas import ServicoConciliacaoPlanilhas

from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.services.calculador_resumo_conciliacao import CalculadorResumoConciliacao
from app.infrastructure.readers.leitor_planilha_excel import LeitorPlanilhaExcel
from app.infrastructure.transformers.conversor_dataframe_registros import ConversorDataFrameRegistros
from app.infrastructure.transformers.conversor_resultados_dataframe import ConversorResultadosDataFrame


def criar_configuracao() -> ConfiguracaoConciliacao:
    """Cria a configuração usada na execução manual."""

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
    """Executa manualmente o fluxo completo de conciliação."""

    caminho_vendas = (Path("data") / "entrada" / "vendas.xlsx")

    caminho_pagamentos = (Path("data") / "entrada"/ "pagamentos.xlsx")

    servico = ServicoConciliacaoPlanilhas(
        leitor=LeitorPlanilhaExcel(),
        conversor=ConversorDataFrameRegistros(),
        calculador_resumo=CalculadorResumoConciliacao(),
        conversor_resultados=ConversorResultadosDataFrame(),
    )

    execucao = servico.executar(
        configuracao=criar_configuracao(),
        caminho_vendas=caminho_vendas,
        caminho_pagamentos=caminho_pagamentos,
        aba_vendas="Vendas",
        aba_pagamentos="Pagamentos",
    )

    print()
    print("=" * 60)
    print("RESULTADOS DA CONCILIAÇÃO")
    print("=" * 60)

    for resultado in execucao.resultados:
        print("-" * 60)

        print(
            f"Chave: "
            f"{resultado.grupo.chave}"
        )

        print(
            f"Status: "
            f"{resultado.status.value}"
        )

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

        print(
            f"Mensagem: "
            f"{resultado.mensagem}"
        )

    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)

    print(
        f"Grupos analisados: "
        f"{execucao.resumo.quantidade_grupos}"
    )

    print(
        f"Grupos conciliados: "
        f"{execucao.resumo.quantidade_conciliados}"
    )

    print(
        f"Grupos não conciliados: "
        f"{execucao.resumo.quantidade_nao_conciliados}"
    )

    print(
        f"Percentual conciliado: "
        f"{execucao.resumo.percentual_conciliado}%"
    )

    print(
        f"Total previsto: "
        f"R$ {execucao.resumo.total_previsto:.2f}"
    )

    print(
        f"Total pago: "
        f"R$ {execucao.resumo.total_pago:.2f}"
    )

    print(
        f"Diferença total: "
        f"R$ {execucao.resumo.diferenca_total:.2f}"
    )

    print()
    print("=" * 60)
    print("DATAFRAME DOS RESULTADOS")
    print("=" * 60)

    print(
        execucao.dataframe_resultados.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    executar()