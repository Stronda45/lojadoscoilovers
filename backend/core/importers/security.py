"""Validação de segurança do upload de catálogo (Fase 2, task 04). Ver
docs/EXCEL-IMPORT.md, seção "Segurança do upload" — checklist implementado
aqui, chamado antes de qualquer parser processar o arquivo."""

import io
import zipfile

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB — cobre os arquivos por categoria
# da MTS (max ~85MB) e TA Technix/rodas com folga. O master da MTS (206MB)
# fica fora de propósito — ver docs/EXCEL-IMPORT.md ("item à parte").
MAX_UNCOMPRESSED_ZIP_SIZE = 300 * 1024 * 1024  # protecao contra zip bomb

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".zip"}


class UploadValidationError(Exception):
    """Arquivo rejeitado antes de qualquer parsing — mensagem já pronta pra
    mostrar pro usuário (não é stack trace)."""


def validate_upload(filename: str, size: int, head_bytes: bytes) -> str:
    """Valida extensão, tamanho e assinatura real do conteúdo. Devolve a
    extensão validada (ex: ".csv"). Levanta UploadValidationError se algo
    não bater — nunca deixa passar pro parser sem checar."""
    name_lower = filename.lower()
    ext = next((e for e in ALLOWED_EXTENSIONS if name_lower.endswith(e)), None)
    if ext is None:
        raise UploadValidationError(
            f"Tipo de arquivo não permitido ({filename}). Só .csv, .xlsx ou .zip."
        )

    if size > MAX_UPLOAD_SIZE:
        mb = MAX_UPLOAD_SIZE // (1024 * 1024)
        raise UploadValidationError(
            f"Arquivo muito grande ({size / 1024 / 1024:.0f}MB, limite {mb}MB). "
            "Se for a MTS, use os arquivos por categoria, não o arquivo master."
        )

    _validate_signature(ext, head_bytes, filename)
    return ext


def _validate_signature(ext: str, head_bytes: bytes, filename: str) -> None:
    """Confere que o conteúdo real bate com a extensão — não confia só no
    nome do arquivo (alguém pode renomear qualquer coisa pra .csv)."""
    if ext in (".xlsx", ".zip"):
        # Ambos sao containers ZIP (xlsx e um .xlsm/.exe renomeado tambem
        # comecam diferente) — assinatura ZIP real e "PK\x03\x04" (ou
        # variantes PK\x05\x06/PK\x07\x08 pra zip vazio/spanned).
        if not head_bytes.startswith(b"PK"):
            raise UploadValidationError(
                f"Conteúdo de {filename} não é um arquivo {ext} válido (assinatura não bate)."
            )
    elif ext == ".csv":
        # CSV e texto puro — rejeita se parecer binario (bytes nulos = sinal
        # de executavel/binario renomeado, nao texto real).
        if b"\x00" in head_bytes:
            raise UploadValidationError(f"{filename} não parece ser um CSV de texto válido.")


def safe_read_zip_member(zip_bytes: bytes, name_contains: str) -> bytes:
    """Lê o conteúdo de um membro dentro de um zip cujo nome contém
    `name_contains`, **sem nunca escrever nada em disco** — elimina o risco
    de path traversal por completo (não tem caminho de arquivo malicioso pra
    sanitizar se nunca criamos arquivo). Também protege contra zip bomb
    (checa tamanho descomprimido antes de ler).

    Casamento por substring (não nome exato) porque nomes de export mudam a
    cada arquivo novo do fornecedor (data/id no nome) — ex: TA Technix
    exporta "TA Technix Preisliste CSV_Export <id> <data>.csv", só
    "Preisliste" é estável entre exports."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        total_uncompressed = sum(info.file_size for info in zf.infolist())
        if total_uncompressed > MAX_UNCOMPRESSED_ZIP_SIZE:
            raise UploadValidationError(
                "Arquivo zip descomprime pra mais do que o limite permitido — rejeitado."
            )

        member = next(
            (info for info in zf.infolist() if name_contains in info.filename),
            None,
        )
        if member is None:
            raise UploadValidationError(
                f"Não encontrei um arquivo com '{name_contains}' no nome dentro do zip."
            )
        return zf.read(member)
