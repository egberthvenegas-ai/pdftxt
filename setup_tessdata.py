#!/usr/bin/env python3
"""Descarga los paquetes de idioma de Tesseract (eng, spa) a la carpeta local tessdata/.

Evita depender de permisos de administrador para escribir en la carpeta
tessdata de la instalacion de Tesseract en Program Files.
"""

import urllib.request
from pathlib import Path

LANGS = ["eng", "spa"]
BASE_URL = "https://github.com/tesseract-ocr/tessdata/raw/main/{lang}.traineddata"
TARGET_DIR = Path(__file__).parent / "tessdata"


def main() -> None:
    TARGET_DIR.mkdir(exist_ok=True)
    for lang in LANGS:
        target = TARGET_DIR / f"{lang}.traineddata"
        if target.exists():
            print(f"Ya existe: {target}")
            continue
        url = BASE_URL.format(lang=lang)
        print(f"Descargando {url} -> {target}")
        urllib.request.urlretrieve(url, target)
    print("Listo.")


if __name__ == "__main__":
    main()
