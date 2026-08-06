from pathlib import Path 
import pandas as pd

COLUNA_LINHA_ORIGEM = "__linha_origem__"

class LeitorPlanilhaExcel:

    EXTENSOES_PERMITIDAS = {".xlsx"}

    def ler(self, caminho_arquivo: str | Path, aba: str | int = 0) -> pd.DataFrame:

        caminho = Path(caminho_arquivo)

        self._validar_caminho(caminho)
        aba_normalizada = self._normalizar_aba(aba)

        try: 
            dataframe = pd.read_excel(io=caminho, sheet_name=aba_normalizada, engine="openpyxl")
        except ImportError as erro:
            raise RuntimeError("A biblioteca openpyxl precisa estar instalada para ler arquivos excel.") from erro
        except ValueError as erro:
            raise ValueError(f"Não foi possivel ler a aba {aba_normalizada} do arquivo {caminho.name}") from erro
        except OSError as erro:
            raise OSError(f"Não foi possivel abrir o arquivo '{caminho}'.") from erro 

        dataframe = self._normalizar_dataframe(dataframe)

        if dataframe.empty:
            raise ValueError("A planilha não possui registros para leitura.")

        return dataframe

    def _validar_caminho(self, caminho: Path) -> None:

        if not caminho.exists():
            raise FileNotFoundError(f"O caminho '{caminho}' não existe.")

        if caminho.is_dir():
            raise ValueError("O caminho deve ser um arquivo e não uma pasta.")

        extensao = caminho.suffix.lower()

        if extensao not in self.EXTENSOES_PERMITIDAS:
            raise ValueError("A extensão deve ser '.xlsx'.")

    def _normalizar_aba(self, aba: str | int = 0) -> str | int:

        if isinstance(aba, bool) or not isinstance(aba, (str, int)):
            raise TypeError("A aba informada deve ser um texto, ou um numero inteiro.")

        if isinstance(aba, str):
            aba = aba.strip()

            if not aba:
                raise ValueError("A aba não pode estar vazia.")

        if isinstance(aba, int):

            if aba < 0:
                raise ValueError("A aba tem que ser um numero maior ou igual a 0.")

        return aba 


    def _normalizar_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe.columns = [str(coluna).strip() for coluna in dataframe.columns]
        dataframe = dataframe.dropna(how="all").copy()

        dataframe[COLUNA_LINHA_ORIGEM] = (
            dataframe.index + 2
        )
        
        dataframe = dataframe.reset_index(drop=True)

        return dataframe
    

        




