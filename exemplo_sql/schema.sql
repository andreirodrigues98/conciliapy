/*
    ConciliaPy
    Script de criação da estrutura do banco de dados SQL Server.

    Este arquivo pode ser executado no SQL Server Management Studio (SSMS)
    para reproduzir a estrutura utilizada pela aplicação.
*/


/* ============================================================
   1. BANCO DE DADOS
   ============================================================ */

IF DB_ID(N'ConciliaPy') IS NULL
BEGIN
    CREATE DATABASE ConciliaPy;
END;
GO


USE ConciliaPy;
GO


/* ============================================================
   2. TABELA DE CONCILIAÇÕES
   ============================================================ */

IF OBJECT_ID(
    N'dbo.Conciliacoes',
    N'U'
) IS NULL
BEGIN

    CREATE TABLE dbo.Conciliacoes (
        Id INT IDENTITY(1,1) PRIMARY KEY,

        Nome NVARCHAR(150) NOT NULL,

        TipoEntrada NVARCHAR(30) NOT NULL,

        DataExecucao DATETIME2
            NOT NULL
            DEFAULT SYSDATETIME(),

        Tolerancia DECIMAL(18,2) NOT NULL,

        ArquivoVendas NVARCHAR(255) NOT NULL,

        ArquivoPagamentos NVARCHAR(255) NOT NULL,

        QuantidadeGrupos INT NOT NULL,

        QuantidadeConciliados INT NOT NULL,

        TotalPrevisto DECIMAL(18,2) NOT NULL,

        TotalPago DECIMAL(18,2) NOT NULL,

        DiferencaTotal DECIMAL(18,2) NOT NULL,

        PercentualConciliado DECIMAL(5,2) NOT NULL
    );

END;
GO


/* ============================================================
   3. TABELA DE RESULTADOS
   ============================================================ */

IF OBJECT_ID(
    N'dbo.ResultadosConciliacao',
    N'U'
) IS NULL
BEGIN

    CREATE TABLE dbo.ResultadosConciliacao (
        Id INT IDENTITY(1,1) PRIMARY KEY,

        ConciliacaoId INT NOT NULL,

        Chave NVARCHAR(200) NOT NULL,

        Status NVARCHAR(50) NOT NULL,

        TotalPrevisto DECIMAL(18,2) NOT NULL,

        TotalPago DECIMAL(18,2) NOT NULL,

        Diferenca DECIMAL(18,2) NOT NULL,

        QuantidadePrevisoes INT NOT NULL,

        QuantidadePagamentos INT NOT NULL,

        Mensagem NVARCHAR(500) NOT NULL,

        CONSTRAINT
            FK_ResultadosConciliacao_Conciliacoes

            FOREIGN KEY (ConciliacaoId)

            REFERENCES dbo.Conciliacoes(Id)
    );

END;
GO