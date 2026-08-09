# ConciliaPy

Sistema de conciliação financeira desenvolvido em Python para comparar dados de vendas e pagamentos provenientes de planilhas Excel, identificar divergências e armazenar o histórico das execuções em SQL Server.

O projeto foi desenvolvido com foco em organização de código, regras de negócio, processamento de dados, persistência relacional e interface web.

---

## Visão geral

Em rotinas financeiras é comum existir uma fonte contendo valores previstos e outra contendo os pagamentos efetivamente realizados.

O ConciliaPy automatiza essa comparação.

A aplicação permite:

- importar dados de um único arquivo Excel com duas abas;
- importar dois arquivos Excel separados;
- mapear dinamicamente as colunas das planilhas;
- definir uma tolerância financeira para conciliação;
- identificar diferentes situações de pagamento;
- visualizar indicadores e resultados detalhados;
- exportar o resultado para Excel;
- armazenar cada execução no SQL Server;
- consultar posteriormente o histórico das conciliações.

---

## Funcionalidades

### Entrada de dados

A aplicação aceita arquivos `.xlsx` em dois formatos:

**Um arquivo Excel**

```text
conciliacao.xlsx
├── Vendas
└── Pagamentos
```

**Dois arquivos Excel**

```text
vendas.xlsx
pagamentos.xlsx
```

As colunas não precisam possuir nomes fixos.

A própria interface permite mapear as colunas da planilha para os campos utilizados internamente pelo sistema.

---

## Regras de conciliação

Os registros são agrupados pela chave de conciliação e classificados conforme a relação entre o valor previsto e o valor pago.

Os principais status são:

| Status | Descrição |
|---|---|
| `CONCILIADO` | Valor pago igual ao valor previsto |
| `CONCILIADO_COM_TOLERANCIA` | Diferença dentro da tolerância configurada |
| `PAGAMENTO_PARCIAL` | Valor pago inferior ao previsto |
| `PAGAMENTO_EXCEDENTE` | Valor pago superior ao previsto |
| `VENDA_SEM_PAGAMENTO` | Venda sem pagamento correspondente |
| `PAGAMENTO_SEM_VENDA` | Pagamento sem venda correspondente |

A diferença é calculada por:

```text
Diferença = Total Pago - Total Previsto
```

---

## Interface

A interface foi desenvolvida com Streamlit.

O fluxo principal é:

```text
Upload dos arquivos
        ↓
Seleção das abas
        ↓
Mapeamento das colunas
        ↓
Configuração da tolerância
        ↓
Conciliação
        ↓
Resumo financeiro
        ↓
Resultados detalhados
        ↓
Persistência no SQL Server
```

A aplicação também possui uma área de histórico que permite consultar conciliações anteriormente armazenadas no banco.

---

## Persistência no SQL Server

Cada execução gera um registro na tabela:

```text
dbo.Conciliacoes
```

e seus resultados são armazenados em:

```text
dbo.ResultadosConciliacao
```

O relacionamento é:

```text
Conciliacoes
     1
     │
     │
     N
     ↓
ResultadosConciliacao
```

A tabela de resultados utiliza uma chave estrangeira para identificar a execução à qual cada resultado pertence.

O acesso ao banco é realizado utilizando:

```text
SQLAlchemy
    ↓
pyodbc
    ↓
ODBC Driver
    ↓
SQL Server
```

---

## Arquitetura

O projeto foi organizado em camadas para separar responsabilidades.

```text
app/
├── application/
├── domain/
├── infrastructure/
└── interface/
```

### Domain

Contém as regras de negócio da conciliação.

Entre suas responsabilidades estão:

- registros financeiros;
- grupos de conciliação;
- classificação dos resultados;
- cálculo de diferenças;
- cálculo do resumo financeiro.

### Application

Coordena os casos de uso da aplicação.

Exemplos:

```text
executar conciliação
salvar histórico
consultar histórico
```

### Infrastructure

Contém implementações relacionadas a recursos externos:

```text
Excel
SQL Server
SQLAlchemy
relatórios
transformação de DataFrames
```

### Interface

Responsável pela interação com o usuário através do Streamlit.

O fluxo de dependências pode ser resumido como:

```text
Interface
    ↓
Application
    ↓
Domain

Infrastructure
    ↓
Banco / Excel / arquivos
```

---

## Tecnologias utilizadas

- Python
- Pandas
- OpenPyXL
- Streamlit
- SQL Server
- SQLAlchemy
- pyodbc
- python-dotenv
- pytest

---

## Estrutura do projeto

```text
conciliapy/
│
├── app/
│   ├── application/
│   │   ├── models/
│   │   └── services/
│   │
│   ├── domain/
│   │   ├── enums/
│   │   ├── models/
│   │   └── services/
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   ├── readers/
│   │   ├── reports/
│   │   └── transformers/
│   │
│   └── interface/
│       ├── adapters/
│       └── streamlit_app.py
│
├── data/
│   ├── entrada/
│   └── saida/
│
├── exemplo_sql/
│   ├── schema.sql
│   ├── dados_exemplo.sql
│   └── consultas_exemplo.sql
│
├── scripts/
│   └── testar_conexao_sql_server.py
│
├── tests/
│
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

---

## Planilhas de demonstração

O projeto contém arquivos fictícios para demonstração em:

```text
data/entrada/
```

Arquivos disponíveis:

```text
vendas_empresa_demo.xlsx
pagamentos_empresa_demo.xlsx
conciliacao_empresa_demo.xlsx
```

Os dados são sintéticos e foram criados exclusivamente para demonstrar o funcionamento da aplicação.

O conjunto contém diferentes cenários de conciliação, incluindo:

- pagamentos exatos;
- pagamentos divididos;
- diferenças dentro da tolerância;
- pagamentos parciais;
- pagamentos excedentes;
- vendas sem pagamento;
- pagamentos sem venda correspondente.

---

## Banco de dados de demonstração

A pasta:

```text
exemplo_sql/
```

contém scripts para reproduzir e explorar a estrutura do banco.

### `schema.sql`

Cria:

```text
ConciliaPy
├── dbo.Conciliacoes
└── dbo.ResultadosConciliacao
```

incluindo:

- `PRIMARY KEY`;
- `FOREIGN KEY`;
- relacionamento 1:N;
- `IDENTITY`;
- `DECIMAL`;
- `DATETIME2`;
- restrições `NOT NULL`.

### `dados_exemplo.sql`

Insere registros fictícios para demonstração.

### `consultas_exemplo.sql`

Contém exemplos utilizando:

```text
SELECT
WHERE
INNER JOIN
COUNT
SUM
GROUP BY
ORDER BY
```

---

# Como executar o projeto

## 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd conciliapy
```

---

## 2. Crie o ambiente virtual

Windows:

```powershell
python -m venv .venv
```

Ative:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Instale as dependências

```powershell
python -m pip install -r requirements.txt
```

Para executar também os testes:

```powershell
python -m pip install -r requirements-dev.txt
```

---

## 4. Configure o SQL Server

O projeto foi desenvolvido utilizando SQL Server.

Execute primeiro:

```text
exemplo_sql/schema.sql
```

no SQL Server Management Studio para criar o banco e suas tabelas.

É necessário possuir um driver ODBC compatível com SQL Server instalado no ambiente.

---

## 5. Configure as variáveis de ambiente

Crie um arquivo:

```text
.env
```

na raiz do projeto.

Exemplo de configuração para SQL Server Express com autenticação do Windows:

```env
SQL_SERVER=.\SQLEXPRESS
SQL_DATABASE=ConciliaPy
SQL_DRIVER=ODBC Driver 18 for SQL Server
SQL_TRUSTED_CONNECTION=yes
SQL_ENCRYPT=yes
SQL_TRUST_SERVER_CERTIFICATE=yes
```

O arquivo `.env` é ignorado pelo Git e não deve ser versionado.

As configurações de certificado acima são destinadas ao ambiente de desenvolvimento local e devem ser revisadas em uma implantação externa.

---

## 6. Teste a conexão com o banco

```powershell
python -m scripts.testar_conexao_sql_server
```

Resultado esperado:

```text
Conexão realizada com sucesso: ConciliaPy
```

---

## 7. Execute a aplicação

```powershell
streamlit run app/interface/streamlit_app.py
```

O Streamlit abrirá a aplicação no navegador.

---

# Exemplo de utilização

Para testar rapidamente o sistema, utilize:

```text
data/entrada/vendas_empresa_demo.xlsx
```

como arquivo de vendas e:

```text
data/entrada/pagamentos_empresa_demo.xlsx
```

como arquivo de pagamentos.

Mapeamento sugerido:

### Vendas

| Campo interno | Coluna |
|---|---|
| Identificador | Nº Documento |
| Cliente | Cliente |
| Data | Data Emissão |
| Valor previsto | Valor Previsto |

### Pagamentos

| Campo interno | Coluna |
|---|---|
| Identificador | Documento Origem |
| Cliente | Cliente |
| Data | Data Pagamento |
| Valor pago | Valor Recebido |

Após configurar os campos, basta executar a conciliação.

---

# Relatório Excel

Após a execução, a aplicação permite gerar um relatório `.xlsx`.

O relatório contém:

```text
Resumo
Resultados
```

O resumo apresenta os principais indicadores financeiros da execução, enquanto a segunda aba contém os resultados detalhados por chave de conciliação.

---

# Histórico

As execuções realizadas podem ser persistidas no SQL Server.

A área **Histórico** da aplicação permite:

- listar execuções anteriores;
- identificar data e nome da execução;
- visualizar indicadores;
- consultar os arquivos utilizados;
- visualizar todos os resultados daquela conciliação.

Isso permite utilizar o banco como histórico e trilha das conciliações já processadas.

---

# Testes

Os testes automatizados utilizam `pytest`.

Para executar:

```powershell
python -m pytest -v
```

Os testes cobrem componentes como:

- regras de domínio;
- transformação de dados;
- cálculo do resumo;
- geração de DataFrames;
- geração de relatórios;
- adaptadores;
- configuração da aplicação.

---

# Decisões técnicas

Algumas decisões adotadas no desenvolvimento:

### `Decimal` para valores financeiros

Valores monetários são tratados com `Decimal` em vez de `float`, reduzindo problemas relacionados à representação binária de números decimais.

### Separação entre domínio e infraestrutura

As regras de conciliação não conhecem SQL Server, Streamlit ou arquivos Excel.

Isso permite que a lógica central seja utilizada independentemente da interface ou forma de persistência.

### Repository para persistência

O acesso ao SQL Server é centralizado no repositório, evitando espalhar consultas ou sessões do SQLAlchemy pela aplicação.

### Transações

A persistência de uma conciliação e de seus resultados ocorre dentro de uma transação.

A execução deve ser armazenada de forma consistente: pai e resultados pertencem à mesma operação.

### Mapeamento dinâmico

A aplicação não exige nomes fixos nas planilhas.

O usuário informa pela interface qual coluna representa cada informação esperada pelo sistema.

---

# Possíveis evoluções

Algumas melhorias possíveis para versões futuras:

- suporte a arquivos CSV;
- múltiplas estratégias de chave de conciliação;
- autenticação de usuários;
- filtros avançados no histórico;
- dashboards financeiros;
- exportação adicional em PDF;
- paginação do histórico;
- migrations de banco utilizando Alembic;
- implantação em ambiente cloud;
- banco SQL Server/Azure SQL remoto;
- processamento de volumes maiores de dados.

---

## Objetivo do projeto

O ConciliaPy foi desenvolvido como projeto de portfólio para aplicar, em um problema próximo de um cenário empresarial:

```text
Python
programação orientada a objetos
Pandas
tratamento de Excel
arquitetura em camadas
testes automatizados
Streamlit
SQL
SQL Server
modelagem relacional
SQLAlchemy ORM
persistência
transações
Git e GitHub
```

Desenvolvido por Andrei Rodrigues

O foco não está apenas na conciliação financeira, mas também na construção de uma aplicação organizada, extensível e com responsabilidades bem definidas.