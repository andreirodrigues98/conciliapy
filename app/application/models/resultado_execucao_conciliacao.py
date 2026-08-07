import pandas as pd
from dataclasses import dataclass


from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao
from app.domain.services.calculador_resumo_conciliacao import ResumoConciliacao

@dataclass
class ResultadoExecucaoConciliacao:

    resultados: list[ResultadoGrupoConciliacao]
    resumo: ResumoConciliacao
    dataframe_resultados: pd.DataFrame