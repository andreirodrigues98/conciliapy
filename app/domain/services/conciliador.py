
from app.domain.enums.status_conciliacao import StatusConciliacao
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.grupo_conciliacao import GrupoConciliacao
from app.domain.models.resultado_grupo_conciliacao import ResultadoGrupoConciliacao


class Conciliador:

    def __init__(self, configuracao: ConfiguracaoConciliacao) -> None:

        if not isinstance(configuracao, ConfiguracaoConciliacao):
            raise TypeError("A configuração deve ser uma instância de ConfiguracaoConciliacao.")

        self.configuracao = configuracao

    def conciliar_grupo(self, grupo: GrupoConciliacao) -> ResultadoGrupoConciliacao:

        if not isinstance(grupo, GrupoConciliacao):
            raise TypeError("O grupo deve ser uma instância de GrupoConciliacao.")

        status = self._classificar_grupo(grupo)
        mensagem = self._criar_mensagem_grupo(status=status, grupo=grupo)

        return ResultadoGrupoConciliacao(grupo, status, mensagem)

    def conciliar_grupos(self, grupos: list[GrupoConciliacao]) -> list[ResultadoGrupoConciliacao]:

        if not isinstance(grupos, list):
            raise TypeError("Os grupos devem ser uma lista de GrupoConciliacao.")
        
        if not grupos:
            raise ValueError("As listas de grupos não piodem estar vazias.")

        resultados = []

        for grupo in grupos:
            resultado = self.conciliar_grupo(grupo)
            resultados.append(resultado)
        
        return resultados
    
    def _criar_mensagem_grupo(self, status: StatusConciliacao, grupo: GrupoConciliacao) -> str:

        diferenca_absoluta = abs(grupo.diferenca)

        if status == StatusConciliacao.PAGAMENTO_SEM_VENDA:
            return (
                f"Pagamento de R$ {grupo.total_pago:.2f} "
                "encontrado sem venda correspondente."
            )

        if status == StatusConciliacao.VENDA_SEM_PAGAMENTO:
            return (
                f"Venda de R$ {grupo.total_previsto:.2f} "
                "encontrada sem pagamento correspondente."
            )

        if status == StatusConciliacao.CONCILIADO:
            return (
                f"Total previsto e total pago são iguais: "
                f"R$ {grupo.total_pago:.2f}."
            )

        if status == StatusConciliacao.CONCILIADO_COM_TOLERANCIA:
            return (
                f"Diferença de R$ {diferenca_absoluta:.2f} "
                "dentro da tolerância configurada."
            )

        if status == StatusConciliacao.PAGAMENTO_PARCIAL:
            return (
                f"Pagamento parcial. "
                f"Faltam R$ {diferenca_absoluta:.2f}."
            )

        if status == StatusConciliacao.PAGAMENTO_EXCEDENTE:
            return (
                f"Pagamento excedente em "
                f"R$ {diferenca_absoluta:.2f}."
            )

        return "Os totais apresentam uma divergência não classificada."

    def _classificar_grupo(self, grupo: GrupoConciliacao) -> StatusConciliacao:

        if not grupo.previsoes:
            return StatusConciliacao.PAGAMENTO_SEM_VENDA

        if not grupo.pagamentos:
            return StatusConciliacao.VENDA_SEM_PAGAMENTO

        if grupo.total_pago == grupo.total_previsto:
            return StatusConciliacao.CONCILIADO

        diferenca_absoluta = abs(grupo.diferenca)

        if diferenca_absoluta <= self.configuracao.tolerancia:
            return StatusConciliacao.CONCILIADO_COM_TOLERANCIA

        if grupo.total_pago < grupo.total_previsto:
            return StatusConciliacao.PAGAMENTO_PARCIAL

        if grupo.total_pago > grupo.total_previsto:
            return StatusConciliacao.PAGAMENTO_EXCEDENTE

        return StatusConciliacao.VALOR_DIVERGENTE

    def criar_chave(self, registro: RegistroFinanceiro) -> tuple[object, ...]:

        if not isinstance(registro, RegistroFinanceiro):
            raise TypeError("O registro deve ser uma isntância de RegistroFinanceiro.")

        valores_da_chave = []

        for campo in self.configuracao.chave_conciliacao:

            if not hasattr(registro, campo):
                raise ValueError(f"O campo {campo} não existe em registro.")

            valor = getattr(registro, campo)

            if valor is None:
                raise ValueError("A chave não pode usar um valor ausente.")

            if isinstance(valor, str):
                valor = valor.strip()

                if not valor:
                    raise ValueError("O valor não pode estar vazio.")

            valores_da_chave.append(valor)

        return tuple(valores_da_chave)

    def indexar_registros(self, registros: list[RegistroFinanceiro]) -> dict[tuple[object, ...], list[RegistroFinanceiro]]:
        """Agrupa registros pela chave de conciliacao configurada"""
        
        if not isinstance(registros, list):
            raise TypeError("Os registros devem ser uma lista.")  

        if not registros:
            raise ValueError("A lista de registros não pode estar vazia.")

        indice = {}

        for registro in registros: 
            chave = self.criar_chave(registro)

            if chave not in indice:
                indice[chave] = []

            indice[chave].append(registro)

        return indice 

    def criar_grupos(self, previsoes: list[RegistroFinanceiro], pagamentos: list[RegistroFinanceiro]) -> list[GrupoConciliacao]:

        if not isinstance(previsoes, list):
            raise TypeError("As previsões precisam ser uma lista.")

        if not isinstance(pagamentos, list):
            raise TypeError("Os pagamentos precisam ser uma lista.")

        if not previsoes and not pagamentos:
            raise ValueError("As listas não podem estar vazias.")

        if previsoes:
            indice_previsoes = self.indexar_registros(previsoes)
        else:
            indice_previsoes = {}

        if pagamentos:
            indice_pagamentos = self.indexar_registros(pagamentos)
        else:
            indice_pagamentos = {}

        chaves_previsoes = set(indice_previsoes.keys())
        chaves_pagamentos = set(indice_pagamentos.keys())

        todas_as_chaves = chaves_previsoes | chaves_pagamentos

        grupos = []

        for chave in todas_as_chaves:
            grupo = GrupoConciliacao(
                chave=chave,
                previsoes=indice_previsoes.get(chave, []),
                pagamentos=indice_pagamentos.get(chave, []),
            )

            grupos.append(grupo)

        return grupos










