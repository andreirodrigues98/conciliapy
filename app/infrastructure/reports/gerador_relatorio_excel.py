from openpyxl import Workbook
from openpyxl.styles import Font

from pathlib import Path

from app.application.models.resultado_execucao_conciliacao import ResultadoExecucaoConciliacao

class GeradorRelatorioExcel:


    def gerar(self, execucao: ResultadoExecucaoConciliacao, caminho_saida: str | Path) -> Path:

        if not isinstance(execucao, ResultadoExecucaoConciliacao):
            raise TypeError("Execução deve ser uma instância de ResultadoExecucaoConciliacao.")

        caminho = Path(caminho_saida)

        if caminho.suffix.lower() != ".xlsx":
            raise ValueError("O caminho deve terminar com '.xlsx'.")

        caminho.parent.mkdir(parents=True, exist_ok=True) 

        wb = Workbook()

        aba_resumo = wb.active
        aba_resumo.title = "Resumo"
        self._criar_aba_resumo(aba_resumo, execucao)

        aba_resultados = wb.create_sheet(title="Resultados")
        self._criar_aba_resultados(aba_resultados, execucao)

        wb.save(caminho)

        return caminho

    def _criar_aba_resumo(self, worksheet, execucao: ResultadoExecucaoConciliacao) -> None:

        resumo = execucao.resumo

        worksheet["A1"] = "Resumo da Conciliação"
        worksheet["A1"].font = Font(bold=True)

        worksheet.append(["Grupos analisados", resumo.quantidade_grupos])
        worksheet.append(["Grupos conciliados", resumo.quantidade_conciliados])
        worksheet.append(["Grupos não conciliados", resumo.quantidade_nao_conciliados])
        worksheet.append(["Percentual conciliado", resumo.percentual_conciliado])
        worksheet.append(["Total previsto", resumo.total_previsto])
        worksheet.append(["Total pago", resumo.total_pago])
        worksheet.append(["Diferença total", float(resumo.diferenca_total)])
        worksheet.append([])
        worksheet.append(["Contagem por Status", "Quantidade"])

        for status, quantidade in resumo.contagem_por_status.items():

            worksheet.append([status.value, quantidade])

    def _criar_aba_resultados(self, worksheet, execucao: ResultadoExecucaoConciliacao) -> None:

        dataframe = execucao.dataframe_resultados

        worksheet.append(list(dataframe.columns))

        for linha in dataframe.itertuples(index=False, name=None):
            worksheet.append(list(linha))

    def _ajustar_largura_colunas(self, worksheet) -> None:

        for coluna in worksheet.columns:

            maior_tamanho = 0

            letra_coluna = coluna[0].column_letter

            for celula in coluna:
                if celula.value is None:
                    continue 

                texto = str(celula.value)

                if len(texto) > maior_tamanho:
                    maior_tamanho = len(texto)

            worksheet.column_dimensions[letra_coluna].width = maior_tamanho + 2



