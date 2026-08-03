from datetime import date
from decimal import Decimal


from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.models.resultado_conciliacao import ResultadoConciliacao
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.services.conciliador import Conciliador


def iniciar_aplicacao() -> None:
    configuracao = ConfiguracaoConciliacao(
    nome="Conciliação por pedido",
    tipo_entrada=TipoEntrada.DUAS_PLANILHAS,
    chave_conciliacao=("identificador",),
    tolerancia=Decimal("0.05"),
    )

    previsoes = [
    RegistroFinanceiro(
        identificador="PED-101",
        cliente="Ana Silva",
        data=date(2026, 1, 5),
        valor_previsto=Decimal("300.00"),
        valor_pago=Decimal("0.00"),
        arquivo_origem="vendas.xlsx",
        linha_origem=2,
    ),
    RegistroFinanceiro(
        identificador="PED-102",
        cliente="Carlos Souza",
        data=date(2026, 1, 6),
        valor_previsto=Decimal("200.00"),
        valor_pago=Decimal("0.00"),
        arquivo_origem="vendas.xlsx",
        linha_origem=3,
    ),
    ]

    pagamentos = [
    RegistroFinanceiro(
        identificador="PED-101",
        cliente="Ana Silva",
        data=date(2026, 1, 10),
        valor_previsto=Decimal("0.00"),
        valor_pago=Decimal("100.00"),
        arquivo_origem="pagamentos.xlsx",
        linha_origem=2,
    ),
    RegistroFinanceiro(
        identificador="PED-101",
        cliente="Ana Silva",
        data=date(2026, 1, 15),
        valor_previsto=Decimal("0.00"),
        valor_pago=Decimal("200.00"),
        arquivo_origem="pagamentos.xlsx",
        linha_origem=3,
    ),
    RegistroFinanceiro(
        identificador="PED-103",
        cliente="Marina Lima",
        data=date(2026, 1, 20),
        valor_previsto=Decimal("0.00"),
        valor_pago=Decimal("500.00"),
        arquivo_origem="pagamentos.xlsx",
        linha_origem=4,
    ),
    ]

    conciliador = Conciliador(configuracao=configuracao)

    grupos = conciliador.criar_grupos(
        previsoes=previsoes,
        pagamentos=pagamentos,
    )

    for grupo in grupos:
        print("-" * 50)
        print(f"Chave: {grupo.chave}")
        print(f"Previsões encontradas: {len(grupo.previsoes)}")
        print(f"Pagamentos encontrados: {len(grupo.pagamentos)}")
        print(f"Total previsto: R$ {grupo.total_previsto:.2f}")
        print(f"Total pago: R$ {grupo.total_pago:.2f}")
        print(f"Diferença: R$ {grupo.diferenca:.2f}")