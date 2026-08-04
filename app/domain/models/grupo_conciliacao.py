from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.models.registro_financeiro import RegistroFinanceiro


@dataclass
class GrupoConciliacao:

    chave: tuple[object,...]
    previsoes: list[RegistroFinanceiro] = field(default_factory=list)
    pagamentos: list[RegistroFinanceiro] = field(default_factory=list)

    def __post_init__(self) -> None:

        if not isinstance(self.chave, tuple):
            raise TypeError("A chave deve ser uma tupla.")

        if not self.chave:
            raise ValueError("A chave não pode estar vazia.")

        if not isinstance(self.previsoes, list):
            raise TypeError("As previsões devem ser uma lista.")

        for previsao in self.previsoes:
            if not isinstance(previsao, RegistroFinanceiro):
                raise TypeError("A previsão deve ser uma instância de RegistroFinanceiro.")

        if not isinstance(self.pagamentos, list):
            raise TypeError("Os pagamentos devem ser uma lista.")
        
        for pagamento in self.pagamentos:
            if not isinstance(pagamento, RegistroFinanceiro):
                raise TypeError("O pagamento deve ser uma instância de RegistroFinanceiro.")

        if not self.previsoes and not self.pagamentos:
            raise ValueError( "O grupo precisa possuir pelo menos uma previsão "
                "ou um pagamento.")
        

        self.previsoes = list(self.previsoes)
        self.pagamentos = list(self.pagamentos)

    @property
    def total_previsto(self) -> Decimal:
        total = Decimal("0.00")

        for previsao in self.previsoes:
            total += previsao.valor_previsto

        return total

    @property
    def total_pago(self) -> Decimal:
        total = Decimal("0.00")

        for pagamento in self.pagamentos:
            total += pagamento.valor_pago
        
        return total

    @property
    def diferenca(self) -> Decimal:
       return self.total_pago - self.total_previsto

    

    
        

        
        










