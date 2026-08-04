from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.enums.tipo_entrada import TipoEntrada

@dataclass
class ConfiguracaoConciliacao:

    nome: str
    tipo_entrada: TipoEntrada
    chave_conciliacao: tuple[str, ...]
    tolerancia: Decimal = Decimal("0.00")
    mapeamento_vendas: dict[str, str] = field(default_factory=dict)
    mapeamento_pagamentos: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:

        if not isinstance(self.nome, str):
            raise TypeError("O nome da configuração deve ser um texto.")

        self.nome = self.nome.strip()

        if not self.nome:
            raise ValueError("O nome da configuração não deve ser vazio.")

        if not isinstance(self.tipo_entrada, TipoEntrada):
            raise TypeError("O tipo de entrada deve ser um objeto de TipoEntrada.")

        if not isinstance(self.chave_conciliacao, tuple):
            raise TypeError("A chave deve ser uma tupla de string.")

        if not self.chave_conciliacao:
            raise ValueError("A chave não pode estar vazia.")

        chave_normalizada = []

        for campo in self.chave_conciliacao:
            if not isinstance(campo, str):
                raise TypeError("O campo deve ser uma string.")

            campo = campo.strip()

            if not campo:
                raise ValueError("O campo não pode estar vazio.")

            chave_normalizada.append(campo)

        self.chave_conciliacao = tuple(chave_normalizada)

        if not isinstance(self.tolerancia, Decimal):
            raise TypeError("A tolerância deve ser decimal.")

        if self.tolerancia < Decimal("0.00"):
            raise ValueError("A tolerância deve ser maior ou igual a 0.")

        self.mapeamento_vendas = self._normalizar_mapeamento(self.mapeamento_vendas, "mapeamento de vendas",)
        self.mapeamento_pagamentos = self._normalizar_mapeamento(self.mapeamento_pagamentos, "mapeamento de pagamentos",)

    def _normalizar_mapeamento(self, mapeamento: dict[str, str], nome_mapeamento: str) -> dict[str, str]:

        if not isinstance(mapeamento, dict):
            raise TypeError(f"O {nome_mapeamento} deve ser um dicionario")
        
        mapeamento_normalizado = {}

        for campo_interno, coluna_origem in mapeamento.items():

            if not isinstance(campo_interno, str):
                raise TypeError("O campo interno deve ser um string.")

            if not isinstance(coluna_origem, str):
                raise TypeError("A coluna de origem deve ser uma string.")

            campo_interno = campo_interno.strip()
            coluna_origem = coluna_origem.strip()

            if not campo_interno:
                raise ValueError("O campo interno não pode estar vazio.")

            if not coluna_origem:
                raise ValueError("A coluna de origem não pode estar vazia.")

            mapeamento_normalizado[campo_interno] = coluna_origem

        return mapeamento_normalizado
            


        




    




