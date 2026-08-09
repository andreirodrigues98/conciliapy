/*
    ConciliaPy
    Consultas de exemplo para análise do histórico
    de conciliações no SQL Server.
*/

USE ConciliaPy;
GO


/* ============================================================
   1. ÚLTIMAS CONCILIAÇÕES
   ============================================================ */

SELECT
    Id,
    Nome,
    TipoEntrada,
    DataExecucao,
    QuantidadeGrupos,
    QuantidadeConciliados,
    PercentualConciliado
FROM dbo.Conciliacoes
ORDER BY DataExecucao DESC;
GO


/* ============================================================
   2. DETALHES DE CADA CONCILIAÇÃO
   ============================================================ */

SELECT
    c.Id AS ConciliacaoId,
    c.Nome,
    c.DataExecucao,
    r.Chave,
    r.Status,
    r.TotalPrevisto,
    r.TotalPago,
    r.Diferenca,
    r.Mensagem
FROM dbo.Conciliacoes AS c
INNER JOIN dbo.ResultadosConciliacao AS r
    ON r.ConciliacaoId = c.Id
ORDER BY
    c.DataExecucao DESC,
    r.Id;
GO


/* ============================================================
   3. QUANTIDADE DE RESULTADOS POR STATUS
   ============================================================ */

SELECT
    Status,
    COUNT(*) AS Quantidade
FROM dbo.ResultadosConciliacao
GROUP BY Status
ORDER BY Quantidade DESC;
GO


/* ============================================================
   4. TOTAIS FINANCEIROS POR CONCILIAÇÃO
   ============================================================ */

SELECT
    Id,
    Nome,
    TotalPrevisto,
    TotalPago,
    DiferencaTotal,
    PercentualConciliado
FROM dbo.Conciliacoes
ORDER BY DataExecucao DESC;
GO


/* ============================================================
   5. TOTAL PREVISTO E PAGO DOS RESULTADOS
   ============================================================ */

SELECT
    ConciliacaoId,
    SUM(TotalPrevisto) AS TotalPrevistoResultados,
    SUM(TotalPago) AS TotalPagoResultados,
    SUM(Diferenca) AS DiferencaResultados
FROM dbo.ResultadosConciliacao
GROUP BY ConciliacaoId
ORDER BY ConciliacaoId DESC;
GO


/* ============================================================
   6. RESULTADOS NÃO CONCILIADOS
   ============================================================ */

SELECT
    ConciliacaoId,
    Chave,
    Status,
    TotalPrevisto,
    TotalPago,
    Diferenca
FROM dbo.ResultadosConciliacao
WHERE Status NOT IN (
    N'CONCILIADO',
    N'CONCILIADO_COM_TOLERANCIA'
)
ORDER BY
    ConciliacaoId DESC,
    ABS(Diferenca) DESC;
GO


/* ============================================================
   7. PAGAMENTOS PARCIAIS
   ============================================================ */

SELECT
    ConciliacaoId,
    Chave,
    TotalPrevisto,
    TotalPago,
    Diferenca
FROM dbo.ResultadosConciliacao
WHERE Status = N'PAGAMENTO_PARCIAL'
ORDER BY Diferenca ASC;
GO


/* ============================================================
   8. PAGAMENTOS EXCEDENTES
   ============================================================ */

SELECT
    ConciliacaoId,
    Chave,
    TotalPrevisto,
    TotalPago,
    Diferenca
FROM dbo.ResultadosConciliacao
WHERE Status = N'PAGAMENTO_EXCEDENTE'
ORDER BY Diferenca DESC;
GO


/* ============================================================
   9. CONCILIAÇÕES COM MENOR PERCENTUAL
   ============================================================ */

SELECT
    Id,
    Nome,
    DataExecucao,
    QuantidadeGrupos,
    QuantidadeConciliados,
    PercentualConciliado
FROM dbo.Conciliacoes
ORDER BY PercentualConciliado ASC;
GO


/* ============================================================
   10. RESUMO POR EXECUÇÃO E STATUS
   ============================================================ */

SELECT
    c.Id AS ConciliacaoId,
    c.Nome,
    r.Status,
    COUNT(*) AS QuantidadeResultados,
    SUM(r.TotalPrevisto) AS TotalPrevisto,
    SUM(r.TotalPago) AS TotalPago,
    SUM(r.Diferenca) AS DiferencaTotal
FROM dbo.Conciliacoes AS c
INNER JOIN dbo.ResultadosConciliacao AS r
    ON r.ConciliacaoId = c.Id
GROUP BY
    c.Id,
    c.Nome,
    r.Status
ORDER BY
    c.Id DESC,
    r.Status;
GO