import tempfile
from pathlib import Path


class AdaptadorUploadTemporario:

    def salvar(self, conteudo: bytes, nome_arquivo: str, diretorio: str | Path | None=None) -> Path:
        
        if not isinstance(conteudo, bytes):
            raise TypeError("O conteudo deve ser do tipo byte.")

        if not conteudo:
            raise ValueError("O conteudo não pode estar vazio.")

        if not isinstance(nome_arquivo, str):
            raise TypeError("O nome do arquivo deve ser do tipo string.")
        
        nome = nome_arquivo.strip()

        if not nome_arquivo:
            raise ValueError("O nome do arquivo não pode estar vazio.") 

        extensao = Path(nome).suffix.lower()

        if extensao != ".xlsx":
            raise ValueError("A extensão do arquivo deve ser '.xlsx'.")

        diretorio_temporario = None

        if not diretorio is None:
            diretorio_temporario = Path(diretorio)

        with tempfile.NamedTemporaryFile(suffix=extensao, delete=False, dir=diretorio_temporario) as arquivo_temporario:
            arquivo_temporario.write(conteudo)
            caminho_temporario = Path(arquivo_temporario.name)

        return caminho_temporario


    def remover(self, caminho: str | Path) -> None:

        caminho_temporario = Path(caminho)

        if caminho_temporario.exists():
            caminho_temporario.unlink()










