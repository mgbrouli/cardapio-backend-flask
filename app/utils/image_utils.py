"""Validação mínima de imagens raster enviadas por usuários."""

from pathlib import Path

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def validate_image_content(filename, content):
    extension = Path(filename).suffix.lower()
    signatures = {
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
    }
    if extension in {".webp", ".avif"}:
        if extension == ".webp":
            valid = (
                len(content) >= 12
                and content[:4] == b"RIFF"
                and content[8:12] == b"WEBP"
            )
        else:
            valid = (
                len(content) >= 12
                and content[4:8] == b"ftyp"
                and content[8:12] in {b"avif", b"avis"}
            )
    elif extension in signatures:
        valid = content.startswith(signatures[extension][0])
    else:
        raise ValueError("Use uma imagem JPG, PNG, WEBP ou AVIF")

    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError("A imagem deve ter no máximo 5 MB")
    if not valid:
        raise ValueError("O conteúdo do arquivo não corresponde a uma imagem válida")
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".avif": "image/avif",
    }[extension]
