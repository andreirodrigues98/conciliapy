from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Identity, Integer, Numeric, Unicode, text

from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.resultado_conciliacao_model import ResultadoConciliacaoModel

class ConciliacaoModel(Base):

    __tablename__ = "Conciliacoes"
    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column("Id", Integer, Identity(start=1, increment=1), primary_key=True)

    nome: Mapped[str] = mapped_column("Nome", Unicode(150), nullable=False)

    tipo_entrada: Mapped[str] = mapped_column("TipoEntrada", Unicode(30), nullable=False)

    data_execucao: Mapped[datetime] = mapped_column("DataExecucao", DATETIME2, nullable=False, server_default=text( "SYSDATETIME()"))

    tolerancia: Mapped[Decimal] = mapped_column("Tolerancia", Numeric(18, 2), nullable=False)

    arquivo_vendas: Mapped[str] = mapped_column("ArquivoVendas", Unicode(255), nullable=False)

    arquivo_pagamentos: Mapped[str] = mapped_column("ArquivoPagamentos", Unicode(255), nullable=False)

    quantidade_grupos: Mapped[int] = mapped_column("QuantidadeGrupos", Integer, nullable=False)
    quantidade_conciliados: Mapped[int] = mapped_column("QuantidadeConciliados", Integer, nullable=False)

    total_previsto: Mapped[Decimal] = mapped_column("TotalPrevisto", Numeric(18, 2), nullable=False)

    total_pago: Mapped[Decimal] = mapped_column("TotalPago", Numeric(18, 2), nullable=False)

    diferenca_total: Mapped[Decimal] = mapped_column("DiferencaTotal", Numeric(18, 2),  nullable=False)

    percentual_conciliado: Mapped[Decimal] = mapped_column("PercentualConciliado", Numeric(5, 2), nullable=False)

    resultados: Mapped[list["ResultadoConciliacaoModel"]] = relationship(back_populates="conciliacao")