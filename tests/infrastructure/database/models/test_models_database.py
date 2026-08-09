from sqlalchemy import inspect
from sqlalchemy.dialects.mssql import DATETIME2

from app.infrastructure.database.models import ConciliacaoModel, ResultadoConciliacaoModel


def test_conciliacao_model_mapeia_tabela_correta() -> None:

    tabela = inspect(ConciliacaoModel).local_table

    assert tabela.name == "Conciliacoes"
    assert tabela.schema == "dbo"

    colunas_esperadas = {
        "Id",
        "Nome",
        "TipoEntrada",
        "DataExecucao",
        "Tolerancia",
        "ArquivoVendas",
        "ArquivoPagamentos",
        "QuantidadeGrupos",
        "QuantidadeConciliados",
        "TotalPrevisto",
        "TotalPago",
        "DiferencaTotal",
        "PercentualConciliado",
    }

    assert colunas_esperadas.issubset(set(tabela.columns.keys()))


def test_data_execucao_usa_datetime2() -> None:

    tabela = inspect(ConciliacaoModel).local_table

    coluna = tabela.columns["DataExecucao"]

    assert isinstance(coluna.type, DATETIME2)


def test_conciliacao_model_possui_chave_primaria() -> None:

    tabela = inspect(ConciliacaoModel).local_table

    colunas_pk = [coluna.name for coluna in tabela.primary_key.columns]

    assert colunas_pk == ["Id"]


def test_resultado_model_possui_foreign_key() -> None:

    tabela = inspect(ResultadoConciliacaoModel).local_table

    foreign_keys = list(tabela.foreign_keys)

    assert len(foreign_keys) == 1

    foreign_key = foreign_keys[0]

    assert foreign_key.parent.name == "ConciliacaoId"

    assert  foreign_key.target_fullname == "dbo.Conciliacoes.Id"


def test_models_possuem_relacionamento_um_para_muitos() -> None:

    relacionamento_resultados = inspect(ConciliacaoModel).relationships["resultados"]

    relacionamento_conciliacao = inspect(ResultadoConciliacaoModel).relationships["conciliacao"]

    assert relacionamento_resultados.back_populates == "conciliacao"
    assert relacionamento_conciliacao.back_populates == "resultados"
    assert relacionamento_resultados.uselist is True
    assert relacionamento_conciliacao.uselist is False