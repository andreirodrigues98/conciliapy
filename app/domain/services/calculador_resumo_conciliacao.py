from decimal import Decimal

from app.domain.models.resumo_conciliacao import ResumoConciliacao
from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao

STATUS_CONCILIADOS = (
    StatusConciliacao.CONCILIADO, StatusConciliacao.CONCILIADO_COM_TOLERANCIA
)

class CalculadorResumoConciliacao:

    def calcular(self, resultados: list[ResultadoGrupoConciliacao]) -> ResumoConciliacao:

        self._validar_resultados(resultados)

        quantidade_grupos = len(resultados)

        quantidade_conciliados = 0
        total_pago = Decimal("0.00")
        total_previsto = Decimal("0.00")

        contagem_por_status = {status: 0 for status in StatusConciliacao}

        for resultado in resultados:
            total_previsto += resultado.total_previsto
            total_pago += resultado.total_pago

            status = resultado.status

            if status in contagem_por_status:
                contagem_por_status[status] += 1

            if status in STATUS_CONCILIADOS:
                quantidade_conciliados += 1

        percentual_conciliado = self._calcular_percentual_conciliado(quantidade_conciliados, quantidade_grupos)

        return ResumoConciliacao(
            quantidade_grupos= quantidade_grupos,
            quantidade_conciliados= quantidade_conciliados,
            total_previsto= total_previsto,
            total_pago= total_pago,
            percentual_conciliado= percentual_conciliado,
            contagem_por_status= contagem_por_status
        )
            
    def _validar_resultados(self, resultados: list[object]) -> None:

        if not isinstance(resultados, list):
            raise TypeError("Resultados deve ser uma lista.")

        for posicao, resultado in enumerate(resultados):
            if not isinstance(resultado, ResultadoGrupoConciliacao):
                raise TypeError(f"O item da posição {posicao} deve ser uma instancia de ResultadoGrupoConciliacao.")

    def _calcular_percentual_conciliado(self, quantidade_conciliado: int, quantidade_grupos: int) -> Decimal:

        if not quantidade_grupos:
            return Decimal("0.00")

        quantidade_conciliado = Decimal(str(quantidade_conciliado))
        quantidade_grupos = Decimal(str(quantidade_grupos))

        percentual = (quantidade_conciliado / quantidade_grupos) * 100

        return percentual.quantize(Decimal("0.01"))
        
