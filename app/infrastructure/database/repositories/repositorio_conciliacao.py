from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.application.models.resultado_execucao_conciliacao import ResultadoExecucaoConciliacao
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao
from app.infrastructure.database.models.conciliacao_model import ConciliacaoModel
from app.infrastructure.database.models.resultado_conciliacao_model import ResultadoConciliacaoModel
from app.application.models.historico_conciliacao import DetalheHistoricoConciliacao, ItemHistoricoConciliacao, ResultadoHistoricoConciliacao 


class RepositorioConciliacao:

    def __init__(self, fabrica_sessoes: sessionmaker[Session]) -> None:
        self._fabrica_sessoes = fabrica_sessoes

    def salvar_execucao(self, configuracao: ConfiguracaoConciliacao,  execucao: ResultadoExecucaoConciliacao, arquivo_vendas: str, arquivo_pagamentos: str) -> int:

        self._validar_dados(configuracao=configuracao, execucao=execucao, arquivo_vendas=arquivo_vendas, arquivo_pagamentos=arquivo_pagamentos)
        

        conciliacao_model = self._criar_conciliacao_model(configuracao=configuracao, execucao=execucao, arquivo_vendas=arquivo_vendas,  arquivo_pagamentos=arquivo_pagamentos)

        for resultado in execucao.resultados:

            resultado_model = (self._criar_resultado_model(resultado=resultado))

            conciliacao_model.resultados.append(resultado_model)

        with self._fabrica_sessoes.begin() as session:

            session.add(conciliacao_model)
            session.flush()
            conciliacao_id = (conciliacao_model.id)

        return conciliacao_id

    def listar_execucoes(self, limite: int = 50,) -> list[ItemHistoricoConciliacao]:

        if isinstance(limite, bool) or not isinstance(limite, int):
            raise TypeError("O limite deve ser um número inteiro.")

        if limite <= 0:
            raise ValueError("O limite deve ser maior que zero.")

        consulta = (select(ConciliacaoModel).order_by(ConciliacaoModel.data_execucao.desc()).limit(limite))

        with self._fabrica_sessoes() as session:
            resultado = session.execute(consulta)
            conciliacoes_orm = (resultado.scalars().all())

            historico = [self._converter_item_historico(conciliacao) for conciliacao in conciliacoes_orm]

        return historico

    def buscar_por_id(self, conciliacao_id: int) -> DetalheHistoricoConciliacao | None:


        if (isinstance(conciliacao_id, bool) or not isinstance(conciliacao_id, int)):

            raise TypeError("O Id da conciliação deve ser um número inteiro.")

        if conciliacao_id <= 0:
            raise ValueError("O Id da conciliação deve ser maior que zero.")

        consulta = (select(ConciliacaoModel).options(selectinload(ConciliacaoModel.resultados)).where(ConciliacaoModel.id == conciliacao_id))

        with self._fabrica_sessoes() as session:
            resultado = session.execute(consulta)

            conciliacao_orm = (resultado.scalars().one_or_none())

            if conciliacao_orm is None:
                return None

            detalhe = (self._converter_detalhe_historico( conciliacao_orm))

        return detalhe

    def _criar_conciliacao_model(self, configuracao: ConfiguracaoConciliacao, execucao: ResultadoExecucaoConciliacao, arquivo_vendas: str, arquivo_pagamentos: str) -> ConciliacaoModel:

        resumo = execucao.resumo

        return ConciliacaoModel(
            nome=configuracao.nome,
            tipo_entrada=(configuracao.tipo_entrada.name),
            tolerancia=configuracao.tolerancia,
            arquivo_vendas=arquivo_vendas.strip(),
            arquivo_pagamentos=(arquivo_pagamentos.strip()),
            quantidade_grupos=(resumo.quantidade_grupos),
            quantidade_conciliados=(resumo.quantidade_conciliados),
            total_previsto=resumo.total_previsto,
            total_pago=resumo.total_pago,
            diferenca_total=resumo.diferenca_total,
            percentual_conciliado=(resumo.percentual_conciliado),
        )

    def _criar_resultado_model(self, resultado: ResultadoGrupoConciliacao) -> ResultadoConciliacaoModel:

        return ResultadoConciliacaoModel(
            chave=self._formatar_chave(resultado.grupo.chave ),
            status=resultado.status.name,
            total_previsto=(resultado.total_previsto),
            total_pago=resultado.total_pago,
            diferenca=resultado.diferenca,
            quantidade_previsoes=len(resultado.grupo.previsoes),
            quantidade_pagamentos=len(resultado.grupo.pagamentos),
            mensagem=resultado.mensagem,
        )

    def _formatar_chave(self, chave: tuple[object, ...]) -> str:

        return " | ".join(str(valor) for valor in chave)

    def _validar_dados(self, configuracao: ConfiguracaoConciliacao, execucao: ResultadoExecucaoConciliacao, arquivo_vendas: str, arquivo_pagamentos: str) -> None:

        if not isinstance(configuracao,  ConfiguracaoConciliacao ):
            raise TypeError("A configuração deve ser uma ConfiguracaoConciliacao.")

        if not isinstance(execucao, ResultadoExecucaoConciliacao):
            raise TypeError("A execução deve ser uma ResultadoExecucaoConciliacao.")

        if not isinstance(arquivo_vendas, str):
            raise TypeError("O nome do arquivo de vendas deve ser uma string.")

        if not arquivo_vendas.strip():
            raise ValueError("O nome do arquivo de vendas não pode estar vazio.")

        if not isinstance(arquivo_pagamentos, str):
            raise TypeError("O nome do arquivo de pagamentos deve ser uma string.")

        if not arquivo_pagamentos.strip():
            raise ValueError("O nome do arquivo de pagamentos não pode estar vazio.")

    def _converter_item_historico(self, conciliacao: ConciliacaoModel) -> ItemHistoricoConciliacao:

        return ItemHistoricoConciliacao(
            id=conciliacao.id,
            nome=conciliacao.nome,
            tipo_entrada=(conciliacao.tipo_entrada),
            data_execucao=(conciliacao.data_execucao),
            quantidade_grupos=(conciliacao.quantidade_grupos),
            quantidade_conciliados=(conciliacao.quantidade_conciliados),
            total_previsto=(conciliacao.total_previsto),
            total_pago=(conciliacao.total_pago),
            diferenca_total=(conciliacao.diferenca_total),
            percentual_conciliado=(conciliacao.percentual_conciliado)
        )

    def _converter_resultado_historico(self, resultado: ResultadoConciliacaoModel) -> ResultadoHistoricoConciliacao:

        return ResultadoHistoricoConciliacao(
            chave=resultado.chave,
            status=resultado.status,
            total_previsto=(resultado.total_previsto),
            total_pago=resultado.total_pago,
            diferenca=resultado.diferenca,
            quantidade_previsoes=(resultado.quantidade_previsoes),
            quantidade_pagamentos=(resultado.quantidade_pagamentos),
            mensagem=resultado.mensagem
        )

    def _converter_detalhe_historico(self, conciliacao: ConciliacaoModel) -> DetalheHistoricoConciliacao:

        resultados = tuple(self._converter_resultado_historico(resultado) for resultado in conciliacao.resultados)

        return DetalheHistoricoConciliacao(
            id=conciliacao.id,
            nome=conciliacao.nome,
            tipo_entrada=conciliacao.tipo_entrada,
            data_execucao=conciliacao.data_execucao,
            quantidade_grupos=(conciliacao.quantidade_grupos),
            quantidade_conciliados=(conciliacao.quantidade_conciliados),
            total_previsto=(conciliacao.total_previsto),
            total_pago=conciliacao.total_pago,
            diferenca_total=(conciliacao.diferenca_total),
            percentual_conciliado=(conciliacao.percentual_conciliado),
            tolerancia=conciliacao.tolerancia,
            arquivo_vendas=(conciliacao.arquivo_vendas),
            arquivo_pagamentos=(conciliacao.arquivo_pagamentos),
            resultados=resultados
        )




