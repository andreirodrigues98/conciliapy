from enum import Enum

class StatusConciliacao(Enum):
    """Representa os status e uma conciliação"""

    CONCILIADO = "Conciliado"
    CONCILIADO_COM_TOLERANCIA = "Conciliado com Tolerância"
    VALOR_DIVERGENTE = "Valor Divergente"
    PAGAMENTO_PARCIAL = "Pagamento parcial"
    PAGAMENTO_EXCEDENTE = "Pagamento excedente"
    PAGAMENTO_NAO_ENCONTRADO = "Pagamento não encontrado"
    VENDA_SEM_PAGAMENTO = "Venda sem pagamento"
    PAGAMENTO_SEM_VENDA = "Pagamento sem venda"
    PAGAMENTO_DUPLICADO = "Pagamento duplicado"
    VENDA_DUPLICADA = "Venda duplicada"
    REGISTRO_DUPLICADO = "Registro duplicado"
    REGISTRO_INVALIDO = "Registro inválido"
    IDENTIFICADOR_AUSENTE = "Identificador ausente"
    CLIENTE_AUSENTE = "Cliente ausente"
    DATA_INVALIDA = "Data inválida"
    VALOR_INVALIDO = "Valor inválido"
    NAO_CONCILIADO = "Não conciliado"





