from typing import Protocol

from app.application.models.historico_conciliacao import DetalheHistoricoConciliacao, ItemHistoricoConciliacao
from app.application.models.resultado_execucao_conciliacao import ResultadoExecucaoConciliacao
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao


class RepositorioHistoricoProtocol(Protocol):

    def salvar_execucao(self, configuracao: ConfiguracaoConciliacao, execucao: ResultadoExecucaoConciliacao, arquivo_vendas: str, arquivo_pagamentos: str) -> int:
        ...

    def listar_execucoes(self, limite: int = 50) -> list[ItemHistoricoConciliacao]:
        ...

    def buscar_por_id(self,conciliacao_id: int) -> DetalheHistoricoConciliacao | None:
        ...


class ServicoHistoricoConciliacao:

    def __init__(self, repositorio: RepositorioHistoricoProtocol) -> None:
        self._repositorio = repositorio

    def salvar_execucao(self, configuracao: ConfiguracaoConciliacao, execucao: ResultadoExecucaoConciliacao, arquivo_vendas: str, arquivo_pagamentos: str,) -> int:

        return self._repositorio.salvar_execucao(
            configuracao=configuracao,
            execucao=execucao,
            arquivo_vendas=arquivo_vendas,
            arquivo_pagamentos=arquivo_pagamentos,
        )

    def listar_historico(self, limite: int = 50) -> list[ItemHistoricoConciliacao]:

        return self._repositorio.listar_execucoes(limite=limite)

    def buscar_execucao(self, conciliacao_id: int) -> DetalheHistoricoConciliacao | None:


        return self._repositorio.buscar_por_id(conciliacao_id=conciliacao_id)