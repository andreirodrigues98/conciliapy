from datetime import date
from decimal import Decimal

import pytest

from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.services.conciliador import Conciliador


def criar_configuracao(
    chave_conciliacao: tuple[str, ...] = ("identificador",),
    tolerancia: Decimal = Decimal("0.05"),
) -> ConfiguracaoConciliacao:
    """Cria uma configuração padrão para os testes."""

    return ConfiguracaoConciliacao(
        nome="Configuração de teste",
        tipo_entrada=TipoEntrada.DUAS_PLANILHAS,
        chave_conciliacao=chave_conciliacao,
        tolerancia=tolerancia,
    )


def criar_registro(
    identificador: str,
    cliente: str = "Cliente Teste",
    valor_previsto: Decimal = Decimal("0.00"),
    valor_pago: Decimal = Decimal("0.00"),
    dia: int = 1,
    arquivo_origem: str = "teste.xlsx",
) -> RegistroFinanceiro:
    """Cria um registro financeiro padrão para os testes."""

    return RegistroFinanceiro(
        identificador=identificador,
        cliente=cliente,
        data=date(2026, 1, dia),
        valor_previsto=valor_previsto,
        valor_pago=valor_pago,
        arquivo_origem=arquivo_origem,
        linha_origem=dia + 1,
    )


def test_criar_chave_composta_usa_todos_os_campos() -> None:
    configuracao = criar_configuracao(
        chave_conciliacao=("cliente", "mes", "ano"),
    )

    conciliador = Conciliador(configuracao=configuracao)

    registro = criar_registro(
        identificador="PED-101",
        cliente="Ana Silva",
        dia=5,
    )

    chave = conciliador.criar_chave(registro)

    assert chave == ("Ana Silva", 1, 2026)


def test_indexar_registros_agrupa_registros_com_mesma_chave() -> None:
    configuracao = criar_configuracao(
        chave_conciliacao=("cliente", "mes", "ano"),
    )

    conciliador = Conciliador(configuracao=configuracao)

    registro_ana_1 = criar_registro(
        identificador="PED-101",
        cliente="Ana Silva",
        dia=5,
    )

    registro_ana_2 = criar_registro(
        identificador="PED-102",
        cliente="Ana Silva",
        dia=15,
    )

    registro_carlos = criar_registro(
        identificador="PED-103",
        cliente="Carlos Souza",
        dia=20,
    )

    registros = [
        registro_ana_1,
        registro_ana_2,
        registro_carlos,
    ]

    indice = conciliador.indexar_registros(registros)

    assert len(indice) == 2
    assert indice[("Ana Silva", 1, 2026)] == [
        registro_ana_1,
        registro_ana_2,
    ]
    assert indice[("Carlos Souza", 1, 2026)] == [
        registro_carlos,
    ]


def test_criar_grupos_preserva_registros_dos_dois_lados() -> None:
    configuracao = criar_configuracao()
    conciliador = Conciliador(configuracao=configuracao)

    previsoes = [
        criar_registro(
            identificador="PED-101",
            cliente="Ana Silva",
            valor_previsto=Decimal("300.00"),
            arquivo_origem="vendas.xlsx",
        ),
        criar_registro(
            identificador="PED-102",
            cliente="Carlos Souza",
            valor_previsto=Decimal("200.00"),
            arquivo_origem="vendas.xlsx",
        ),
    ]

    pagamentos = [
        criar_registro(
            identificador="PED-101",
            cliente="Ana Silva",
            valor_pago=Decimal("100.00"),
            arquivo_origem="pagamentos.xlsx",
        ),
        criar_registro(
            identificador="PED-101",
            cliente="Ana Silva",
            valor_pago=Decimal("200.00"),
            arquivo_origem="pagamentos.xlsx",
        ),
        criar_registro(
            identificador="PED-103",
            cliente="Marina Lima",
            valor_pago=Decimal("500.00"),
            arquivo_origem="pagamentos.xlsx",
        ),
    ]

    grupos = conciliador.criar_grupos(
        previsoes=previsoes,
        pagamentos=pagamentos,
    )

    grupos_por_chave = {}

    for grupo in grupos:
        grupos_por_chave[grupo.chave] = grupo

    grupo_101 = grupos_por_chave[("PED-101",)]
    grupo_102 = grupos_por_chave[("PED-102",)]
    grupo_103 = grupos_por_chave[("PED-103",)]

    assert len(grupo_101.previsoes) == 1
    assert len(grupo_101.pagamentos) == 2

    assert len(grupo_102.previsoes) == 1
    assert len(grupo_102.pagamentos) == 0

    assert len(grupo_103.previsoes) == 0
    assert len(grupo_103.pagamentos) == 1


def test_conciliar_grupos_classifica_cenarios_principais() -> None:
    configuracao = criar_configuracao()
    conciliador = Conciliador(configuracao=configuracao)

    previsoes = [
        criar_registro(
            identificador="PED-101",
            valor_previsto=Decimal("300.00"),
            arquivo_origem="vendas.xlsx",
        ),
        criar_registro(
            identificador="PED-102",
            valor_previsto=Decimal("200.00"),
            arquivo_origem="vendas.xlsx",
        ),
    ]

    pagamentos = [
        criar_registro(
            identificador="PED-101",
            valor_pago=Decimal("100.00"),
            arquivo_origem="pagamentos.xlsx",
        ),
        criar_registro(
            identificador="PED-101",
            valor_pago=Decimal("200.00"),
            arquivo_origem="pagamentos.xlsx",
        ),
        criar_registro(
            identificador="PED-103",
            valor_pago=Decimal("500.00"),
            arquivo_origem="pagamentos.xlsx",
        ),
    ]

    grupos = conciliador.criar_grupos(
        previsoes=previsoes,
        pagamentos=pagamentos,
    )

    resultados = conciliador.conciliar_grupos(grupos)

    resultados_por_chave = {}

    for resultado in resultados:
        resultados_por_chave[resultado.grupo.chave] = resultado

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


def test_conciliar_grupo_classifica_pagamento_parcial() -> None:
    configuracao = criar_configuracao()
    conciliador = Conciliador(configuracao=configuracao)

    previsoes = [
        criar_registro(
            identificador="PED-200",
            valor_previsto=Decimal("500.00"),
            arquivo_origem="vendas.xlsx",
        ),
    ]

    pagamentos = [
        criar_registro(
            identificador="PED-200",
            valor_pago=Decimal("300.00"),
            arquivo_origem="pagamentos.xlsx",
        ),
    ]

    grupos = conciliador.criar_grupos(
        previsoes=previsoes,
        pagamentos=pagamentos,
    )

    resultado = conciliador.conciliar_grupo(grupos[0])

    assert resultado.status == StatusConciliacao.PAGAMENTO_PARCIAL
    assert resultado.total_previsto == Decimal("500.00")
    assert resultado.total_pago == Decimal("300.00")
    assert resultado.diferenca == Decimal("-200.00")


def test_conciliar_grupos_rejeita_lista_vazia() -> None:
    configuracao = criar_configuracao()
    conciliador = Conciliador(configuracao=configuracao)

    with pytest.raises(ValueError):
        conciliador.conciliar_grupos([])