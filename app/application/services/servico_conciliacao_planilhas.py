from pathlib import Path

from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao
from app.domain.services.conciliador import Conciliador
from app.infrastructure.readers.leitor_planilha_excel import LeitorPlanilhaExcel
from app.infrastructure.transformers.conversor_dataframe_registros import ConversorDataFrameRegistros


class ServicoConciliacaoPlanilhas:

    def __init__(self, leitor: LeitorPlanilhaExcel, conversor: ConversorDataFrameRegistros) -> None:

        if not isinstance(leitor, LeitorPlanilhaExcel):
            raise TypeError("O leitor deve ser uma instância de LeitorPlanilhaExcel.")

        if not isinstance(conversor, ConversorDataFrameRegistros):
            raise TypeError("O conversor deve ser uma instância de ConversorDataFrameRegistros.")

        self.leitor = leitor
        self.conversor = conversor


    def executar(
            self, 
            configuracao: ConfiguracaoConciliacao, 
            caminho_vendas: str | Path, 
            caminho_pagamentos: str | Path,
            aba_vendas: str,
            aba_pagamentos: str
    ) -> list[ResultadoGrupoConciliacao]:

        self._validar_configuracao(configuracao)

        dataframe_vendas = self.leitor.ler(caminho_vendas, aba_vendas)
        dataframe_pagamentos = self.leitor.ler(caminho_pagamentos, aba_pagamentos)

        previsoes = self.conversor.converter_previsoes(dataframe_vendas, configuracao, caminho_vendas, aba_vendas)
        pagamentos = self.conversor.converter_pagamentos(dataframe_pagamentos, configuracao, caminho_pagamentos, aba_pagamentos)

        conciliador = Conciliador(configuracao)

        grupos = conciliador.criar_grupos(previsoes, pagamentos)

        resultados = conciliador.conciliar_grupos(grupos)

        return resultados

    def _validar_configuracao(self, configuracao: ConfiguracaoConciliacao) -> None:

        if not isinstance(configuracao, ConfiguracaoConciliacao):
            raise TypeError("A configuração deve ser uma instância de ConfiguracaoConciliacao.")

        

        

