import streamlit as st
import pandas as pd
import os

from io import BytesIO
from decimal import Decimal
from tempfile import TemporaryDirectory
from pathlib import Path

from app.application.models.resultado_execucao_conciliacao import ResultadoExecucaoConciliacao
from app.application.services.servico_conciliacao_planilhas import ServicoConciliacaoPlanilhas
from app.domain.enums.tipo_entrada import TipoEntrada
from app.domain.models.configuracao_conciliacao import ConfiguracaoConciliacao
from app.domain.services.calculador_resumo_conciliacao import CalculadorResumoConciliacao
from app.infrastructure.readers.leitor_planilha_excel import LeitorPlanilhaExcel
from app.infrastructure.transformers.conversor_dataframe_registros import ConversorDataFrameRegistros
from app.infrastructure.transformers.conversor_resultados_dataframe import  ConversorResultadosDataFrame
from app.interface.adapters.adaptador_upload_temporario import AdaptadorUploadTemporario
from app.infrastructure.reports.gerador_relatorio_excel import GeradorRelatorioExcel
from app.application.services.servico_historico_conciliacao import ServicoHistoricoConciliacao
from app.infrastructure.database.conexao import criar_engine, criar_fabrica_sessoes
from app.infrastructure.database.repositories.repositorio_conciliacao import RepositorioConciliacao


CAMPOS_VENDAS: dict[str, str] = {
    "identificador": "Identificador da venda",
    "cliente": "Cliente",
    "data": "Data da venda",
    "valor_previsto": "Valor previsto",
}

CAMPOS_PAGAMENTOS: dict[str, str] = {
    "identificador": "Identificador da venda",
    "cliente": "Cliente",
    "data": "Data do pagamento",
    "valor_pago": "Valor pago",
}

def banco_configurado() -> bool:
    return bool(os.getenv("SQL_SERVER") and os.getenv("SQL_DATABASE"))

def exibir_pagina_inicial() -> None:

    st.set_page_config(
        page_title="ConciliaPy",
        page_icon="📊",
        layout="wide"
    )

    st.title("ConciliaPy")

    opcoes_navegacao = ["Nova conciliação"]

    if banco_configurado():
        opcoes_navegacao.append("Histórico")

    pagina = st.sidebar.radio("Navegação", options=opcoes_navegacao)

    servico_historico = None

    if banco_configurado():
        servico_historico = (criar_servico_historico())

    if (pagina == "Histórico" and servico_historico is not None):
        exibir_historico(servico_historico)
        st.stop()

    st.subheader("Sistema Inteligente de Conciliação Financeira")

    st.write(
        """
        Compare planilhas de vendas e pagamentos,
        identifique divergências e visualize os
        resultados da conciliação de forma simples.
        """
    )



    st.divider()

    st.header("Entrada de dados")

    tipo_entrada = st.radio(
        "Como deseja enviar os dados?",
        options=[
            "Um arquivo Excel",
            "Dois arquivos Excel",
        ],
        horizontal=True,
    )

    if tipo_entrada == "Um arquivo Excel":
        exibir_upload_planilha_unica()

    else:
        exibir_upload_duas_planilhas()

def obter_abas_excel(arquivo) -> list[str]:

    excel = pd.ExcelFile(arquivo, engine="openpyxl")

    abas = list(excel.sheet_names)

    excel.close()

    return abas 

def exibir_upload_planilha_unica() -> None:

    st.subheader("Arquivo Conciliação")

    arquivo = st.file_uploader("Selecione o arquivo excel: ", type=["xlsx"], key="arquivo_unico")

    if arquivo is None:
        st.info("O arquivo informado deve conter abas de vendas e pagamentos.")
        return 

    try:
        abas = obter_abas_excel(arquivo)

    except Exception:
        st.error(f"Não foi possível carregar o arquivo")
        return 

    st.success(f"Arquivo carregado: {arquivo.name}")

    if len(abas) < 2:
        st.error(f"O arquivo precisa conter duas abas.")
        return 

    aba_vendas = st.selectbox("Aba de Vendas", options=abas, key="aba_vendas_unico")

    indice_pagamentos = (1 if len(abas) > 1 else 0)

    aba_pagamentos = st.selectbox("Aba de Pagamentos", options=abas, index=indice_pagamentos, key="aba_pagamentos_unico")

    if aba_vendas == aba_pagamentos:
        st.warning("Selecione abas diferentes para vendas e pagamentos.")
        return 

    try:
        colunas_vendas = obter_colunas_excel(arquivo=arquivo, aba=aba_vendas)

        colunas_pagamentos = obter_colunas_excel(arquivo=arquivo, aba=aba_pagamentos)

    except Exception:
        st.error("Não foi possível identificar as colunas das abas selecionadas." )
        return

    st.divider()

    coluna_mapeamento_vendas, coluna_mapeamento_pagamentos = (st.columns(2))

    with coluna_mapeamento_vendas:
        mapeamento_vendas = exibir_mapeamento_colunas(
            titulo="Mapeamento de vendas",
            colunas=colunas_vendas,
            campos=CAMPOS_VENDAS,
            prefixo_key="unico_vendas",
        )

    with coluna_mapeamento_pagamentos:
        mapeamento_pagamentos = exibir_mapeamento_colunas(
            titulo="Mapeamento de pagamentos",
            colunas=colunas_pagamentos,
            campos=CAMPOS_PAGAMENTOS,
            prefixo_key="unico_pagamentos",
        )

    if (mapeamento_vendas is not None and mapeamento_pagamentos is not None):
        st.success("Mapeamento das colunas concluído.")

        exibir_configuracao_execucao(
        tipo_entrada=TipoEntrada.PLANILHA_UNICA,
        arquivo_vendas=arquivo,
        arquivo_pagamentos=arquivo,
        aba_vendas=aba_vendas,
        aba_pagamentos=aba_pagamentos,
        mapeamento_vendas=mapeamento_vendas,
        mapeamento_pagamentos=mapeamento_pagamentos,
        )
        
def exibir_upload_duas_planilhas() -> None:

    st.subheader("Arquivos da conciliação")

    coluna_vendas, coluna_pagamentos = st.columns(2)

    with coluna_vendas:
        arquivo_vendas = st.file_uploader("Arquivo de vendas", type=["xlsx"], key="arquivo_vendas")

    with coluna_pagamentos:
        arquivo_pagamentos = st.file_uploader("Arquivo de pagamentos", type=["xlsx"], key="arquivo_pagamentos")

    if (arquivo_vendas is None or arquivo_pagamentos is None):
        st.info("Envie os arquivos de vendas e pagamentos para continuar.")
        return

    try:
        abas_vendas = obter_abas_excel(arquivo=arquivo_vendas)

        abas_pagamentos = obter_abas_excel( arquivo=arquivo_pagamentos)

    except Exception:
        st.error("Não foi possível identificar as abas dos arquivos.")
        return

    with coluna_vendas:
        st.success(f"Arquivo carregado: {arquivo_vendas.name}" )

        aba_vendas = st.selectbox("Aba de vendas",  options=abas_vendas, key="aba_vendas_duplo")

    with coluna_pagamentos:
        st.success(f"Arquivo carregado: {arquivo_pagamentos.name}" )

        aba_pagamentos = st.selectbox("Aba de pagamentos",  options=abas_pagamentos, key="aba_pagamentos_duplo")

    try:
        colunas_vendas = obter_colunas_excel( arquivo=arquivo_vendas, aba=aba_vendas)

        colunas_pagamentos = obter_colunas_excel(arquivo=arquivo_pagamentos, aba=aba_pagamentos)

    except Exception:
        st.error( "Não foi possível identificar as colunas das abas selecionadas.")
        return

    st.divider()

    coluna_mapeamento_vendas, coluna_mapeamento_pagamentos = st.columns(2)

    with coluna_mapeamento_vendas:
        mapeamento_vendas = exibir_mapeamento_colunas(
            titulo="Mapeamento de vendas",
            colunas=colunas_vendas,
            campos=CAMPOS_VENDAS,
            prefixo_key="duplo_vendas"
        )

    with coluna_mapeamento_pagamentos:
        mapeamento_pagamentos = exibir_mapeamento_colunas(
            titulo="Mapeamento de pagamentos",
            colunas=colunas_pagamentos,
            campos=CAMPOS_PAGAMENTOS,
            prefixo_key="duplo_pagamentos"
        )

    if (mapeamento_vendas is not None and mapeamento_pagamentos is not None):
        st.success("Mapeamento das colunas concluído.")

        exibir_configuracao_execucao(
        tipo_entrada=TipoEntrada.DUAS_PLANILHAS,
        arquivo_vendas=arquivo_vendas,
        arquivo_pagamentos=arquivo_pagamentos,
        aba_vendas=aba_vendas,
        aba_pagamentos=aba_pagamentos,
        mapeamento_vendas=mapeamento_vendas,
        mapeamento_pagamentos=mapeamento_pagamentos,
        )

def obter_colunas_excel(arquivo, aba: str) -> list[str]:

    arquivo_memoria = BytesIO(arquivo.getvalue())

    dataframe_cabecalho = pd.read_excel(arquivo_memoria, aba, engine="openpyxl", nrows=0)

    colunas = [str(coluna).strip() for coluna in dataframe_cabecalho.columns]

    return colunas 

def exibir_mapeamento_colunas(titulo: str, colunas: list[str], campos: dict[str, str], 
                              prefixo_key: str) -> dict[str, str] | None:

    st.subheader(titulo)

    mapeamento: dict[str, str] = {}

    mapeamento_completo = True

    for campo, rotulo in campos.items():

        coluna_selecionada = st.selectbox(rotulo, options=colunas, index=None, placeholder="Selecione uma Coluna:", key=(f"{prefixo_key}_{campo}"))

        if coluna_selecionada is None:
            mapeamento_completo = False
        else:
            mapeamento[campo] = coluna_selecionada

    if not mapeamento_completo:
        return None 

    return mapeamento

def criar_configuracao_interface(nome: str, tipo_entrada: TipoEntrada, tolerancia: Decimal, 
    mapeamento_vendas: dict[str, str], mapeamento_pagamentos: dict[str, str]) -> ConfiguracaoConciliacao:

    return ConfiguracaoConciliacao(
        nome= nome, 
        tipo_entrada=tipo_entrada,
        chave_conciliacao=("identificador",),
        tolerancia=tolerancia,
        mapeamento_vendas=mapeamento_vendas,
        mapeamento_pagamentos=mapeamento_pagamentos
    )

def criar_servico_conciliacao() -> ServicoConciliacaoPlanilhas:

    return ServicoConciliacaoPlanilhas(
        leitor= LeitorPlanilhaExcel(),
        conversor=ConversorDataFrameRegistros(),
        calculador_resumo=CalculadorResumoConciliacao(),
        conversor_resultados=ConversorResultadosDataFrame()
    )

def executar_conciliacao_interface(tipo_entrada: TipoEntrada, arquivo_vendas, arquivo_pagamentos, 
    aba_vendas: str, aba_pagamentos: str, configuracao: ConfiguracaoConciliacao) -> ResultadoExecucaoConciliacao:

    adaptador = AdaptadorUploadTemporario()

    caminhos_temporarios = []

    try:
        if tipo_entrada == TipoEntrada.PLANILHA_UNICA:
            caminho_unico = adaptador.salvar(conteudo=arquivo_vendas.getvalue(), nome_arquivo=arquivo_vendas.name)
            caminhos_temporarios.append(caminho_unico)

            caminho_vendas = caminho_unico
            caminho_pagamentos = caminho_unico

        else:
            caminho_vendas = adaptador.salvar(conteudo=arquivo_vendas.getvalue(), nome_arquivo=arquivo_vendas.name)
            caminhos_temporarios.append(caminho_vendas)
            caminho_pagamentos = adaptador.salvar(conteudo=arquivo_pagamentos.getvalue(), nome_arquivo=arquivo_pagamentos.name)
            caminhos_temporarios.append(caminho_pagamentos)

        servico = criar_servico_conciliacao()

        execucao = servico.executar(
            configuracao=configuracao,
            caminho_vendas=caminho_vendas,
            caminho_pagamentos=caminho_pagamentos,
            aba_vendas=aba_vendas,
            aba_pagamentos=aba_pagamentos,
        )

        return execucao
    finally:
        for caminho in caminhos_temporarios:
            adaptador.remover(caminho=caminho)
    
def exibir_configuracao_execucao(tipo_entrada: TipoEntrada, arquivo_vendas, arquivo_pagamentos, aba_vendas: str, 
    aba_pagamentos: str,  mapeamento_vendas: dict[str, str],  mapeamento_pagamentos: dict[str, str]) -> None:

    st.divider()

    st.header("Configuração da conciliação")

    nome = st.text_input("Nome da conciliação", value="Conciliação", key="nome_conciliacao")

    tolerancia_numero = st.number_input("Tolerância de valores", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="tolerancia_conciliacao")

    executar = st.button("Executar conciliação", type="primary", key="executar_conciliacao")

    if executar:

        try:
            tolerancia = Decimal(str(tolerancia_numero))

            configuracao = criar_configuracao_interface(
                nome=nome,
                tipo_entrada=tipo_entrada,
                tolerancia=tolerancia,
                mapeamento_vendas=mapeamento_vendas,
                mapeamento_pagamentos=mapeamento_pagamentos,
            )

            execucao = executar_conciliacao_interface(
                tipo_entrada=tipo_entrada,
                arquivo_vendas=arquivo_vendas,
                arquivo_pagamentos=arquivo_pagamentos,
                aba_vendas=aba_vendas,
                aba_pagamentos=aba_pagamentos,
                configuracao=configuracao,
            )

        except (TypeError, ValueError):
            st.error(f"Não foi possível executar a conciliação.")
            return

        except Exception:
            st.error("Ocorreu um erro inesperado durante a conciliação.")
            return
        else:
            st.session_state["execucao_conciliacao"] = execucao
            st.session_state.pop("conciliacao_id", None)

            st.success("Conciliação executada com sucesso.")

            if banco_configurado():
                servico_historico = (criar_servico_historico())

                try:
                    conciliacao_id = (
                        servico_historico.salvar_execucao(
                            configuracao=configuracao,
                            execucao=execucao,
                            arquivo_vendas=arquivo_vendas.name,
                            arquivo_pagamentos=(arquivo_pagamentos.name)
                        )
                    )

                    st.session_state["conciliacao_id"] = conciliacao_id

                    st.success(f"Conciliação salva no histórico com Id {conciliacao_id}.")

                except Exception:
                    st.warning("A conciliação foi executada, mas não foi possível salvá-la no histórico.")

    execucao_salva = st.session_state.get("execucao_conciliacao")

    if execucao_salva is not None:
        exibir_resultado_conciliacao(execucao=execucao_salva)
    
def formatar_moeda(valor: Decimal) -> str:
    
    valor_formatado = f"{valor:,.2f}"
    valor_formatado = valor_formatado.replace(",", "_").replace(".", ",").replace("_", ".")

    return f"R$ {valor_formatado}"

def gerar_relatorio_excel_bytes(execucao: ResultadoExecucaoConciliacao) -> bytes:

    with TemporaryDirectory() as diretorio:
        caminho_relatorio = Path(diretorio) / "relatorio_conciliacao.xlsx"

        gerador = GeradorRelatorioExcel()

        caminho_gerado = gerador.gerar(execucao=execucao, caminho_saida=caminho_relatorio)

        conteudo = caminho_gerado.read_bytes()

        return conteudo

def exibir_resultado_conciliacao(execucao: ResultadoExecucaoConciliacao) -> None:

    resumo = execucao.resumo

    st.divider()
    st.header("Resultado Conciliação")

    coluna_grupos, coluna_conciliados, coluna_nao_conciliados, coluna_percentual = st.columns(4)

    with coluna_grupos:
        st.metric(label="Grupos analisados", value=resumo.quantidade_grupos)
    
    with coluna_conciliados:
        st.metric(label="Conciliados", value=resumo.quantidade_conciliados)

    with coluna_nao_conciliados:
        st.metric(label="Não Conciliados", value=resumo.quantidade_nao_conciliados)
        
    with coluna_percentual:
        st.metric(label="Percentual", value= f"{resumo.percentual_conciliado}%")

    coluna_previsto, coluna_pago, coluna_diferenca= st.columns(3)

    with coluna_previsto:
        st.metric(label="Total Previsto", value=formatar_moeda(resumo.total_previsto))
        
    with coluna_pago:
        st.metric(label="Total Pago", value=formatar_moeda(resumo.total_pago))
    
    with coluna_diferenca:
        st.metric(label="Diferença Total", value=formatar_moeda(resumo.diferenca_total))

    st.divider()
    st.subheader("Resultados detalhados")

    st.dataframe(execucao.dataframe_resultados, hide_index=True, width="stretch")

    st.divider()
    st.subheader("Exportação")

    try:
        relatorio_bytes = gerar_relatorio_excel_bytes(execucao=execucao)
    except Exception:
        st.error("Não foi possível gerar o relatório Excel.")   
        return 

    st.download_button(label="Baixar relatório Excel", data=relatorio_bytes, file_name="relatorio_conciliacao.xlsx", 
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")

@st.cache_resource
def criar_servico_historico() -> ServicoHistoricoConciliacao:


    engine = criar_engine()

    fabrica_sessoes = criar_fabrica_sessoes(
        engine=engine
    )

    repositorio = RepositorioConciliacao(
        fabrica_sessoes=fabrica_sessoes
    )

    return ServicoHistoricoConciliacao(
        repositorio=repositorio
    )

def exibir_historico( servico_historico: ServicoHistoricoConciliacao,) -> None:


    st.header(
        "Histórico de conciliações"
    )

    try:
        historico = (
            servico_historico.listar_historico(
                limite=50
            )
        )

    except Exception:
        st.error(
            "Não foi possível consultar "
            "o histórico no banco de dados."
        )
        return

    if not historico:
        st.info(
            "Nenhuma conciliação foi "
            "salva até o momento."
        )
        return

    itens_por_id = {item.id: item for item in historico}

    conciliacao_id = st.selectbox( "Selecione uma execução", options=list(itens_por_id.keys()),
        format_func=lambda item_id: (
            f"#{item_id} - "
            f"{itens_por_id[item_id].nome} - "
            f"{itens_por_id[item_id].data_execucao: %d/%m/%Y %H:%M}"))

    if conciliacao_id is None:
        return

    try:
        detalhe = (servico_historico.buscar_execucao(conciliacao_id))

    except Exception:
        st.error("Não foi possível carregar os detalhes da conciliação.")
        return

    if detalhe is None:
        st.warning("A conciliação selecionada não foi encontrada.")
        return

    st.subheader(
        detalhe.nome
    )

    st.caption(f"Executada em {detalhe.data_execucao: %d/%m/%Y às %H:%M}")

    coluna_1, coluna_2, coluna_3 = (st.columns(3))

    coluna_1.metric("Grupos analisados", detalhe.quantidade_grupos)

    coluna_2.metric("Conciliados", detalhe.quantidade_conciliados)

    coluna_3.metric("Não conciliados", detalhe.quantidade_nao_conciliados)

    coluna_4, coluna_5, coluna_6 = (st.columns(3))

    coluna_4.metric(
        "Total previsto",
        formatar_moeda(
            detalhe.total_previsto
        ),
    )

    coluna_5.metric(
        "Total pago",
        formatar_moeda(
            detalhe.total_pago
        ),
    )

    coluna_6.metric(
        "Diferença",
        formatar_moeda(
            detalhe.diferenca_total
        ),
    )

    st.metric(
        "Percentual conciliado",
        f"{detalhe.percentual_conciliado:.2f}%",
    )

    st.divider()

    st.write(
        f"**Arquivo de vendas:** "
        f"{detalhe.arquivo_vendas}"
    )

    st.write(
        f"**Arquivo de pagamentos:** "
        f"{detalhe.arquivo_pagamentos}"
    )

    st.write(
        f"**Tolerância:** "
        f"{formatar_moeda(detalhe.tolerancia)}"
    )

    st.subheader(
        "Resultados"
    )

    dataframe = pd.DataFrame(
        [
            {
                "Chave": resultado.chave,
                "Status": resultado.status,
                "Total Previsto": (
                    resultado.total_previsto
                ),
                "Total Pago": (
                    resultado.total_pago
                ),
                "Diferença": (
                    resultado.diferenca
                ),
                "Qtd. Previsões": (
                    resultado.quantidade_previsoes
                ),
                "Qtd. Pagamentos": (
                    resultado.quantidade_pagamentos
                ),
                "Mensagem": (
                    resultado.mensagem
                ),
            }
            for resultado
            in detalhe.resultados
        ]
    )

    st.dataframe(
        dataframe,
        hide_index=True,
        width="stretch",
    )

if __name__ == "__main__":
    exibir_pagina_inicial()