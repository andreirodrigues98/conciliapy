/*
    ConciliaPy
    Dados fictícios para demonstração do banco.

    Execute este script somente depois do schema.sql.
*/

USE ConciliaPy;
GO


/* ============================================================
   1. CONCILIAÇÃO DE EXEMPLO
   ============================================================ */

INSERT INTO dbo.Conciliacoes (
    Nome,
    TipoEntrada,
    Tolerancia,
    ArquivoVendas,
    ArquivoPagamentos,
    QuantidadeGrupos,
    QuantidadeConciliados,
    TotalPrevisto,
    TotalPago,
    DiferencaTotal,
    PercentualConciliado
)
VALUES (
    N'Conciliação Demonstrativa',
    N'DUAS_PLANILHAS',
    0.05,
    N'vendas_empresa_demo.xlsx',
    N'pagamentos_empresa_demo.xlsx',
    5,
    2,
    3500.00,
    3050.03,
    -449.97,
    40.00
);
GO


/* ============================================================
   2. RECUPERA O ID CRIADO
   ============================================================ */

DECLARE @ConciliacaoId INT;

SELECT
    @ConciliacaoId = MAX(Id)
FROM dbo.Conciliacoes;
    

/* ============================================================
   3. RESULTADOS DA CONCILIAÇÃO
   ============================================================ */

INSERT INTO dbo.ResultadosConciliacao (
    ConciliacaoId,
    Chave,
    Status,
    TotalPrevisto,
    TotalPago,
    Diferenca,
    QuantidadePrevisoes,
    QuantidadePagamentos,
    Mensagem
)
VALUES

(
    @ConciliacaoId,
    N'NF-2026-000001',
    N'CONCILIADO',
    1000.00,
    1000.00,
    0.00,
    1,
    1,
    N'Valores conciliados.'
),

(
    @ConciliacaoId,
    N'NF-2026-000002',
    N'CONCILIADO_COM_TOLERANCIA',
    500.00,
    500.03,
    0.03,
    1,
    1,
    N'Diferença dentro da tolerância configurada.'
),

(
    @ConciliacaoId,
    N'NF-2026-000003',
    N'PAGAMENTO_PARCIAL',
    800.00,
    600.00,
    -200.00,
    1,
    1,
    N'Pagamento inferior ao valor previsto.'
),

(
    @ConciliacaoId,
    N'NF-2026-000004',
    N'PAGAMENTO_EXCEDENTE',
    700.00,
    950.00,
    250.00,
    1,
    1,
    N'Pagamento superior ao valor previsto.'
),

(
    @ConciliacaoId,
    N'NF-2026-000005',
    N'VENDA_SEM_PAGAMENTO',
    500.00,
    0.00,
    -500.00,
    1,
    0,
    N'Não foi localizado pagamento para a venda.'
);
GO