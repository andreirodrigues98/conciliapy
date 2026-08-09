from decimal import Decimal

from app.domain.enums.tipo_entrada import TipoEntrada
from app.interface.streamlit_app import criar_configuracao_interface


def test_criar_configuracao_interface() -> None:

    mapeamento_vendas = {
        "identificador": "Pedido",
        "cliente": "Cliente",
        "data": "Data",
        "valor_previsto": "Valor",
    }

    mapeamento_pagamentos = {
        "identificador": "Pedido",
        "cliente": "Cliente",
        "data": "Data Pagamento",
        "valor_pago": "Valor Pago",
    }

    configuracao = criar_configuracao_interface(
        nome="Conciliação Agosto",
        tipo_entrada=TipoEntrada.DUAS_PLANILHAS,
        tolerancia=Decimal("0.05"),
        mapeamento_vendas=mapeamento_vendas,
        mapeamento_pagamentos=mapeamento_pagamentos,
    )

    assert configuracao.nome == "Conciliação Agosto"
    assert configuracao.tipo_entrada == TipoEntrada.DUAS_PLANILHAS
    assert configuracao.chave_conciliacao == ("identificador",)
    assert  configuracao.tolerancia == Decimal("0.05")
    assert configuracao.mapeamento_vendas == mapeamento_vendas
    assert configuracao.mapeamento_pagamentos == mapeamento_pagamentos