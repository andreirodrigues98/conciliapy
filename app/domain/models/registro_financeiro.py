from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class RegistroFinanceiro:

    identificador: str
    cliente: str
    data: date
    valor_previsto: Decimal
    valor_pago: Decimal
    arquivo_origem: str
    aba_origem: str | None = None
    linha_origem: int | None = None

    def __post_init__(self) -> None:

        if not isinstance(self.identificador, str):
            raise TypeError("O identificador deve ser um texto")

        if not isinstance(self.cliente, str):
            raise TypeError("O cliente deve ser um texto")

        if not isinstance(self.arquivo_origem, str):
            raise TypeError("O arquivo de origem deve ser um texto")

        self.identificador = self.identificador.strip()
        self.cliente = self.cliente.strip()
        self.arquivo_origem = self.arquivo_origem.strip()

        if not self.identificador:
            raise ValueError("O identifcador não pode estar vazio.")

        if not self.cliente:
            raise ValueError("O cliente não pode estar vazio.")

        if not self.arquivo_origem:
            raise ValueError("O arquivo de origem não pode estar vazio.")

        if self.aba_origem is not None:
            
            if not isinstance(self.aba_origem, str):
                raise TypeError("A aba de origem precisa ser texto.")

            self.aba_origem = self.aba_origem.strip() or None

        if not isinstance(self.data, date):
            raise TypeError("A data precisa ser uma data válida.")

        if not isinstance(self.valor_previsto, Decimal):
            raise TypeError("O valor previsto precisa ser um decimal.")

        if not isinstance(self.valor_pago, Decimal):
            raise TypeError("O valor pago precisa ser um decimal.")

        if self.valor_previsto < 0:
            raise ValueError("O valor precisa ser maior ou igual a 0.")
        if self.valor_pago < 0:
            raise ValueError("O valor precisa ser maior ou igual a 0.")

        if self.linha_origem is not None:
            if not isinstance(self.linha_origem, int):
                raise TypeError("A linha de origem precisa ser um inteiro.")

            if self.linha_origem < 1:
                raise ValueError("A linha de origem precisa ser maior ou igual a 1.")

    @property 
    def mes(self) -> int:
        return self.data.month

    @property
    def ano(self) -> int:
        return self.data.year

    @property
    def diferenca(self) -> Decimal:
        return self.valor_pago - self.valor_previsto

    