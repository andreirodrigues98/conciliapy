from pathlib import Path
from app.infrastructure.readers.leitor_planilha_excel import LeitorPlanilhaExcel


def executar() -> None:

    caminho = (Path("data") / "entrada" / "vendas.xlsx")
    leitor = LeitorPlanilhaExcel()

    dataframe = leitor.ler(caminho_arquivo=caminho, aba=0)

    print("Primeiras linhas: ")
    print(dataframe.head())

    print("Colunas Encontradas: ")
    print(dataframe.columns.tolist())

    print("Quantidade de linhas e colunas: ")
    print(dataframe.shape)

    print("Tipos Identificados: ")
    print(dataframe.dtypes)


if __name__ == "__main__":
    executar()