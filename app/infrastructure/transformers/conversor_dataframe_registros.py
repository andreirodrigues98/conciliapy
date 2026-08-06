from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.models.registro_financeiro import RegistroFinanceiro
from app.infrastructure.readers.leitor_planilha_excel import COLUNA_LINHA_ORIGEM

class ConversorDataFrameRegistros:

    CAMPOS_COMUNS = ("identificador", "cliente", "data")

    def converter_previsoes(self, dataframe: pd.DataFrame, configuracao: ConfiguracaoConciliacao, 
                            arquivo_origem: str | Path, aba_origem: str | None = None ) -> list[RegistroFinanceiro]:

        return self._converter(
            dataframe=dataframe, configuracao= configuracao, mapeamento=configuracao.mapeamento_vendas, 
            campo_monetario="valor_previsto",
            arquivo_origem=arquivo_origem, aba_origem= aba_origem
        )

    def converter_pagamentos(self, dataframe: pd.DataFrame, configuracao: ConfiguracaoConciliacao,
                            arquivo_origem: str | Path, aba_origem: str | None = None ) -> list[RegistroFinanceiro]:

        return self._converter(
                    dataframe=dataframe, configuracao= configuracao, mapeamento=configuracao.mapeamento_pagamentos, 
                    campo_monetario="valor_pago",
                    arquivo_origem=arquivo_origem, aba_origem= aba_origem
                )


    def _converter(self, dataframe: pd.DataFrame, configuracao: ConfiguracaoConciliacao, mapeamento: dict[str, str],
                   campo_monetario: str, arquivo_origem: str | Path, aba_origem: str | None) -> list[RegistroFinanceiro]:

        self._validar_dataframe(dataframe)
        self._validar_configuracao(configuracao)

        arquivo_normalizado = self._normalizar_arquivo_origem(arquivo_origem)
        aba_normalizada = self._normalizar_aba_origem(aba_origem)

        campos_obrigatorios = (*self.CAMPOS_COMUNS, campo_monetario)

        self._validar_mapeamento(dataframe=dataframe, mapeamento=mapeamento, campos_obrigatorios=campos_obrigatorios)

        registros = []

        for indice, linha in dataframe.iterrows():
            linha_origem = self._obter_linha_origem(linha=linha, indice=indice)

            try:
                identificador = self._converter_texto(valor=self._obter_valor(linha=linha, mapeamento=mapeamento, 
                                                    campo_interno="identificador"), nome_campo="identificador")

                cliente = self._converter_texto(valor=self._obter_valor(linha=linha, mapeamento=mapeamento, 
                                                                        campo_interno="cliente"), nome_campo="cliente")

                data_registro = self._converter_data(valor=self._obter_valor(linha=linha, mapeamento=mapeamento, 
                                                                        campo_interno="data"))

                valor_monetario = self._converter_decimal(valor=self._obter_valor(linha=linha, mapeamento=mapeamento, campo_interno=campo_monetario),
                                                          nome_campo=campo_monetario)

                if campo_monetario == "valor_previsto":
                    valor_previsto = valor_monetario
                    valor_pago = Decimal("0.00")
                else:
                    valor_pago = valor_monetario
                    valor_previsto = Decimal("0.00")

                registro = RegistroFinanceiro(
                    identificador=identificador,
                    cliente=cliente,
                    data=data_registro,
                    valor_previsto=valor_previsto,
                    valor_pago=valor_pago,
                    arquivo_origem=arquivo_normalizado,
                    aba_origem=aba_normalizada,
                    linha_origem=linha_origem
                    )
                
            except (TypeError, ValueError) as erro:

                raise ValueError(f"Erro ao converter a linha {linha_origem}, do arquivo {arquivo_origem}: {erro}") from erro 

            registros.append(registro)

        return registros

    def _validar_dataframe(self, dataframe: pd.DataFrame) -> None:

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Os dados devem ser um Dataframe.")

        if dataframe.empty:
            raise ValueError("O Dataframe não possui registros.")


    def _validar_configuracao(self, configuracao: ConfiguracaoConciliacao) -> None:

        if not isinstance(configuracao, ConfiguracaoConciliacao):
            raise TypeError("A configuracao deve ser uma instancia de ConfiguracaoConciliacao.")


    def _validar_mapeamento(self, dataframe: pd.DataFrame, mapeamento: dict[str, str], campos_obrigatorios: tuple[str, ...]) -> None:

        for campo_interno in campos_obrigatorios:

            if campo_interno not in mapeamento:
                raise ValueError(f"O campo interno '{campo_interno}' nao foi configurado no mapeamento.")

            coluna_origem = mapeamento[campo_interno]

            if coluna_origem not in dataframe.columns:
                raise ValueError(f"A coluna '{coluna_origem}' mapeada no '{campo_interno}', não existe no DataFrame.")


    def _obter_valor(self, linha: pd.Series, mapeamento: dict[str, str], campo_interno: str) -> object:

        coluna_origem = mapeamento[campo_interno]

        valor = linha[coluna_origem]

        if pd.isna(valor):
            raise ValueError(f"O {campo_interno} está ausente.")

        return valor

    def _converter_texto(self, valor: object, nome_campo: str) -> str:

        if pd.isna(valor):
            raise ValueError(f"O campo {nome_campo} está ausente.")

        texto = str(valor).strip()

        if not texto:
            raise ValueError(f"O campo '{nome_campo}' não pode estar vazio.")

        return texto

    def _converter_data(self, valor: object) -> date:

        if pd.isna(valor):
            raise ValueError(f"O campo 'data' está ausente.") 

        if isinstance(valor, datetime):
            return valor.date()

        if isinstance(valor, date):
            return valor

        try:
            data_convertida = pd.to_datetime(valor, dayfirst=True, errors="raise")
        except (TypeError, ValueError) as erro:
            raise ValueError(f"O valor '{valor}' não representa uma data válida.")

        return data_convertida.date()

    def _converter_decimal(self, valor: object,  nome_campo: str, ) -> Decimal:

        if pd.isna(valor):
            raise ValueError(
                f"O campo '{nome_campo}' está ausente."
            )

        if isinstance(valor, bool):
            raise TypeError(
                f"O campo '{nome_campo}' não pode ser booleano."
            )

        try:
            if isinstance(valor, Decimal):
                numero_decimal = valor

            elif isinstance(valor, (int, float)):
                numero_decimal = Decimal(str(valor))

            elif isinstance(valor, str):
                texto = valor.strip()
                texto = texto.replace("R$", "")
                texto = texto.replace(" ", "")

                if not texto:
                    raise ValueError(
                        f"O campo '{nome_campo}' não pode estar vazio."
                    )

                if "," in texto and "." in texto:
                    if texto.rfind(",") > texto.rfind("."):
                        texto = texto.replace(".", "")
                        texto = texto.replace(",", ".")
                    else:
                        texto = texto.replace(",", "")

                elif "," in texto:
                    texto = texto.replace(".", "")
                    texto = texto.replace(",", ".")

                numero_decimal = Decimal(texto)

            else:
                raise TypeError(
                    f"O campo '{nome_campo}' possui um tipo inválido."
                )

            return numero_decimal.quantize(
                Decimal("0.01")
            )

        except InvalidOperation as erro:
            raise ValueError(
                f"O valor '{valor}' do campo '{nome_campo}' "
                "não representa um número monetário válido."
            ) from erro
    
    def _obter_linha_origem(self, linha: pd.Series, indice: object) -> int:

        if COLUNA_LINHA_ORIGEM in linha.index:
            valor_linha = linha[COLUNA_LINHA_ORIGEM]

            if not pd.isna(valor_linha):
                return int(valor_linha)

        return int(indice) + 2

    def _normalizar_arquivo_origem(self, arquivo_origem: str | Path) -> str:

        if not isinstance(arquivo_origem, (str, Path)):
            raise TypeError("O arquivo de origem deve ser texto ou Path.")

        nome_arquivo = Path(arquivo_origem).name.strip()

        if not nome_arquivo:
            raise ValueError("O arquivo de origem não pode estar vazio.")

        return nome_arquivo

    def _normalizar_aba_origem( self, aba_origem: str | None) -> str | None:

        if aba_origem is None:
            return None

        if not isinstance(aba_origem, str):
            raise TypeError("A aba de origem deve ser um texto.")

        return aba_origem.strip() or None


            






                











