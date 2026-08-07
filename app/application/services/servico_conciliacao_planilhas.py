from pathlib import Path

from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao
from app.domain.services.conciliador import Conciliador
from app.application.models.resultado_execucao_conciliacao import ResultadoExecucaoConciliacao
from app.domain.services.calculador_resumo_conciliacao import CalculadorResumoConciliacao
from app.infrastructure.transformers.conversor_resultados_dataframe import ConversorResultadosDataFrame
from app.infrastructure.readers.leitor_planilha_excel import LeitorPlanilhaExcel
from app.infrastructure.transformers.conversor_dataframe_registros import ConversorDataFrameRegistros


class ServicoConciliacaoPlanilhas:

    def __init__(self, leitor: LeitorPlanilhaExcel, conversor: ConversorDataFrameRegistros,
                 calculador_resumo: CalculadorResumoConciliacao, conversor_resultados: ConversorResultadosDataFrame) -> None:

        if not isinstance(leitor, LeitorPlanilhaExcel):
            raise TypeError("O leitor deve ser uma instância de LeitorPlanilhaExcel.")

        if not isinstance(conversor, ConversorDataFrameRegistros):
            raise TypeError("O conversor deve ser uma instância de ConversorDataFrameRegistros.")

        if not isinstance(calculador_resumo, CalculadorResumoConciliacao):
            raise TypeError("O calculador deve ser uma instância de CalculadorResumoConciliacao.")

        if not isinstance(conversor_resultados, ConversorResultadosDataFrame):
            raise TypeError("O conversor_resultados deve ser uma instância de ConversorResultadosDataFrame.")

        self.leitor = leitor
        self.conversor = conversor
        self.calculador_resumo = calculador_resumo
        self.conversor_resultados = conversor_resultados

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

        resumo = self.calculador_resumo.calcular(resultados)
        dataframe_resultados = self.conversor_resultados.converter(resultados)

        return ResultadoExecucaoConciliacao(
            resultados=resultados, 
            resumo=resumo,
            dataframe_resultados=dataframe_resultados
        )


    def _validar_configuracao(self, configuracao: ConfiguracaoConciliacao) -> None:

        if not isinstance(configuracao, ConfiguracaoConciliacao):
            raise TypeError("A configuração deve ser uma instância de ConfiguracaoConciliacao.")

        

        

