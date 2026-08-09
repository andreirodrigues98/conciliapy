from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pandas as pd
import pytest

from app.application.models.resultado_execucao_conciliacao import ResultadoExecucaoConciliacao
from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.grupo_conciliacao import GrupoConciliacao
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao
from app.domain.models.resumo_conciliacao import ResumoConciliacao
from app.infrastructure.database.models.conciliacao_model import ConciliacaoModel
from app.infrastructure.database.repositories.repositorio_conciliacao import RepositorioConciliacao


def criar_dados_teste() -> tuple[ConfiguracaoConciliacao, ResultadoExecucaoConciliacao]:

    configuracao = ConfiguracaoConciliacao(
        nome="Teste Banco",
        tipo_entrada=TipoEntrada.DUAS_PLANILHAS,
        chave_conciliacao=(
            "identificador",
        ),
        tolerancia=Decimal("0.05"),
    )

    previsao = RegistroFinanceiro(
        identificador="NF-1",
        cliente="Cliente A",
        data=date(2026, 1, 1),
        valor_previsto=Decimal("100.00"),
        valor_pago=Decimal("0.00"),
        arquivo_origem="vendas.xlsx",
    )

    pagamento = RegistroFinanceiro(
        identificador="NF-1",
        cliente="Cliente A",
        data=date(2026, 1, 2),
        valor_previsto=Decimal("0.00"),
        valor_pago=Decimal("100.00"),
        arquivo_origem="pagamentos.xlsx",
    )

    grupo = GrupoConciliacao(
        chave=("NF-1",),
        previsoes=[previsao],
        pagamentos=[pagamento],
    )

    resultado = ResultadoGrupoConciliacao(
        grupo=grupo,
        status=StatusConciliacao.CONCILIADO,
        mensagem="Valores conciliados.",
    )

    resumo = ResumoConciliacao(
        quantidade_grupos=1,
        quantidade_conciliados=1,
        total_previsto=Decimal("100.00"),
        total_pago=Decimal("100.00"),
        percentual_conciliado=Decimal(
            "100.00"
        ),
        contagem_por_status={
            StatusConciliacao.CONCILIADO: 1,
        },
    )

    execucao = ResultadoExecucaoConciliacao(
        resultados=[resultado],
        resumo=resumo,
        dataframe_resultados=pd.DataFrame(),
    )

    return configuracao, execucao


def criar_fabrica_para_session(sessao):

    contexto = MagicMock()

    contexto.__enter__.return_value = (sessao)

    contexto.__exit__.return_value = False

    fabrica = MagicMock()

    fabrica.return_value = contexto

    return fabrica


def test_formatar_chave_composta() -> None:

    repositorio = RepositorioConciliacao(MagicMock())

    resultado = repositorio._formatar_chave(("NF-1", "Salvador"))

    assert resultado == "NF-1 | Salvador"
    


def test_criar_models_preserva_dados() -> None:

    repositorio = RepositorioConciliacao(MagicMock())

    configuracao, execucao = (criar_dados_teste())

    conciliacao = (
        repositorio._criar_conciliacao_model(configuracao, execucao, " vendas.xlsx ", " pagamentos.xlsx "))

    assert conciliacao.nome == "Teste Banco"
    assert conciliacao.tipo_entrada == "DUAS_PLANILHAS"
    
    assert conciliacao.arquivo_vendas == "vendas.xlsx"
    
    resultado = (repositorio._criar_resultado_model(execucao.resultados[0]))

    assert resultado.chave == "NF-1"
    assert resultado.status == "CONCILIADO"

    assert resultado.total_pago== Decimal("100.00")


def test_salvar_execucao_adiciona_pai_e_filhos_e_retorna_id() -> None:

    configuracao, execucao = (
        criar_dados_teste()
    )

    sessao = MagicMock()

    contexto = MagicMock()

    contexto.__enter__.return_value = (
        sessao
    )

    contexto.__exit__.return_value = False

    fabrica = MagicMock()

    fabrica.begin.return_value = contexto

    def atribuir_id() -> None:

        modelo_salvo = (sessao.add.call_args.args[0])
        modelo_salvo.id = 42

    sessao.flush.side_effect = atribuir_id

    repositorio = RepositorioConciliacao(fabrica)

    conciliacao_id = (
        repositorio.salvar_execucao(
            configuracao=configuracao,
            execucao=execucao,
            arquivo_vendas="vendas.xlsx",
            arquivo_pagamentos=(
                "pagamentos.xlsx"
            )
        )
    )

    assert conciliacao_id == 42

    modelo_salvo = (sessao.add.call_args.args[0])

    assert len(modelo_salvo.resultados) == 1

    assert modelo_salvo.resultados[0].status == "CONCILIADO"
    

    sessao.flush.assert_called_once()


def test_listar_execucoes_retorna_models() -> None:

    conciliacao = ConciliacaoModel(nome="Teste")

    resultado_sql = MagicMock()

    resultado_sql.scalars.return_value.all.return_value = [conciliacao]

    sessao = MagicMock()

    sessao.execute.return_value = (resultado_sql)

    fabrica = criar_fabrica_para_session(sessao)

    repositorio = RepositorioConciliacao(fabrica)

    encontrados = (repositorio.listar_execucoes(limite=10))

    assert encontrados == [conciliacao]

    sessao.execute.assert_called_once()


def test_buscar_por_id_retorna_model() -> None:

    conciliacao = ConciliacaoModel(nome="Teste")

    resultado_sql = MagicMock()

    (resultado_sql.scalars.return_value.one_or_none.return_value) = conciliacao

    sessao = MagicMock()
    sessao.execute.return_value = (resultado_sql)

    fabrica = criar_fabrica_para_session(sessao)

    repositorio = RepositorioConciliacao(fabrica)
    

    encontrado = repositorio.buscar_por_id(1)
    

    assert encontrado is conciliacao


def test_salvar_rejeita_nome_arquivo_vazio() -> None:

    repositorio = RepositorioConciliacao(MagicMock())

    configuracao, execucao = (criar_dados_teste())

    with pytest.raises(ValueError, match="vendas"):
        repositorio.salvar_execucao(configuracao=configuracao, execucao=execucao, arquivo_vendas="   ",   arquivo_pagamentos=("pagamentos.xlsx"))


def test_listar_rejeita_limite_invalido() -> None:

    repositorio = RepositorioConciliacao(MagicMock())

    with pytest.raises(TypeError):
        repositorio.listar_execucoes(True)

    with pytest.raises(ValueError):
        repositorio.listar_execucoes(0)


def test_buscar_rejeita_id_invalido() -> None:

    repositorio = RepositorioConciliacao(MagicMock())

    with pytest.raises(TypeError):
        repositorio.buscar_por_id(True)

    with pytest.raises(ValueError):
        repositorio.buscar_por_id(0)