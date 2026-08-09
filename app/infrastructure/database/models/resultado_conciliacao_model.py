from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, Integer, Numeric,  Unicode
from sqlalchemy.orm import Mapped,  mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.conciliacao_model import ConciliacaoModel


class ResultadoConciliacaoModel(Base):

    __tablename__ = "ResultadosConciliacao"
    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column("Id", Integer, Identity(start=1, increment=1), primary_key=True)

    conciliacao_id: Mapped[int] = mapped_column("ConciliacaoId", Integer, ForeignKey("dbo.Conciliacoes.Id"), nullable=False)
    
    chave: Mapped[str] = mapped_column("Chave", Unicode(200), nullable=False)

    status: Mapped[str] = mapped_column("Status", Unicode(50), nullable=False)

    total_previsto: Mapped[Decimal] = mapped_column("TotalPrevisto", Numeric(18, 2), nullable=False)

    total_pago: Mapped[Decimal] = mapped_column( "TotalPago", Numeric(18, 2), nullable=False)

    diferenca: Mapped[Decimal] = mapped_column("Diferenca", Numeric(18, 2), nullable=False)

    quantidade_previsoes: Mapped[int] = mapped_column("QuantidadePrevisoes", Integer, nullable=False)

    quantidade_pagamentos: Mapped[int] = mapped_column("QuantidadePagamentos",  Integer, nullable=False)

    mensagem: Mapped[str] = mapped_column("Mensagem",  Unicode(500),  nullable=False)

    conciliacao: Mapped["ConciliacaoModel"] = relationship(back_populates="resultados")