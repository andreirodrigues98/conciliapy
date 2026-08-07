from pathlib import Path
import pandas as pd

from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao

COLUNAS_RESULTADO: tuple[str, ...] = (
    "Chave", "Status", "Total Previsto", 
    "Total Pago", "Diferença", "Quantidade de Previsões",
    "Quantidade de Pagamentos", "Mensagem"
)

class ConversorResultadosDataFrame:

    def converter(self, resultados: list[ResultadoGrupoConciliacao]) -> pd.DataFrame:

        self._validar_resultados(resultados)

        linhas = []

        for resultado in resultados:
            linha = self._converter_resultado_para_linha(resultado)
            linhas.append(linha)

        dataframe = pd.DataFrame(data=linhas, columns=COLUNAS_RESULTADO)

        return dataframe

    def _validar_resultados(self, resultados: list[ResultadoGrupoConciliacao]) -> None:

        if not isinstance(resultados, list):
            raise TypeError("Resultados deve ser uma lista.")

        for posicao, resultado in enumerate(resultados):
            if not isinstance(resultado, ResultadoGrupoConciliacao):
                raise TypeError(f"O item da posição {posicao} deve ser uma instância de ResultadoGrupoConciliacao.")

    def _converter_resultado_para_linha(self, resultado: ResultadoGrupoConciliacao) -> dict[str, object]:

        return {
            "Chave": self._formatar_chave(resultado.grupo.chave),
            "Status": resultado.status.value,
            "Total Previsto": float(resultado.total_previsto),
            "Total Pago": float(resultado.total_pago),
            "Diferença": float(resultado.diferenca),
            "Quantidade de Previsões": len(resultado.grupo.previsoes),
            "Quantidade de Pagamentos": len(resultado.grupo.pagamentos),
            "Mensagem": resultado.mensagem
        }
        
    def _formatar_chave(self, chave: tuple[str, ...]) -> str:

        valores_texto = []

        for valor in chave:
            valores_texto.append(str(valor))
        
        return " | ".join(valores_texto)

