from pathlib import Path

import pytest

from app.interface.adapters.adaptador_upload_temporario import AdaptadorUploadTemporario

def test_salvar_cria_arquivo_temporario(tmp_path: Path) -> None:
    
    adaptador = AdaptadorUploadTemporario()

    conteudo = b"conteudo de teste"
    caminho = adaptador.salvar(conteudo=conteudo, nome_arquivo="vendas.xlsx", diretorio=tmp_path)

    assert caminho.exists()
    assert caminho.suffix == ".xlsx"
    assert caminho.read_bytes() == conteudo


def test_salvar_rejeita_conteudo_vazio(tmp_path: Path) -> None:

    adaptador = AdaptadorUploadTemporario()

    with pytest.raises(ValueError, match="não pode estar vazio"):
        adaptador.salvar(conteudo=b"", nome_arquivo="vendas.xlsx", diretorio=tmp_path)


def test_salvar_rejeita_extensao_invalida(tmp_path: Path) -> None:

    adaptador = AdaptadorUploadTemporario()

    with pytest.raises(ValueError, match="\\.xlsx"):
        adaptador.salvar(conteudo=b"conteudo", nome_arquivo="vendas.csv", diretorio=tmp_path)


def test_remover_exclui_arquivo_temporario(tmp_path: Path) -> None:

    adaptador = AdaptadorUploadTemporario()

    caminho = adaptador.salvar(conteudo=b"conteudo", nome_arquivo="vendas.xlsx", diretorio=tmp_path)

    assert caminho.exists()
    adaptador.remover(caminho=caminho)

    assert not caminho.exists()