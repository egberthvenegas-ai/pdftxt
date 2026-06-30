#!/usr/bin/env python3
"""Convierte PDFs (texto o escaneados) a archivos .txt.

Uso:
    python pdf2txt.py                      # procesa todo ./input -> ./output
    python pdf2txt.py archivo.pdf          # procesa un solo archivo
    python pdf2txt.py carpeta/             # procesa todos los PDF de esa carpeta
    python pdf2txt.py archivo.pdf -o out.txt
    python pdf2txt.py -l eng               # fuerza idioma OCR (default: spa+eng)
"""

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageOps

DEFAULT_INPUT_DIR = Path("input")
DEFAULT_OUTPUT_DIR = Path("output")
MIN_CHARS_PER_PAGE = 20  # debajo de esto se asume que la pagina esta escaneada
OCR_ZOOM = 3.0  # factor de escalado al renderizar la pagina para OCR (mas resolucion = mejor OCR)

# Carpeta local con los paquetes de idioma (evita depender de permisos de administrador
# para escribir en la carpeta tessdata de la instalacion de Tesseract en Program Files).
LOCAL_TESSDATA_DIR = Path(__file__).parent / "tessdata"
DEFAULT_TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_for_ocr(img: Image.Image) -> Image.Image:
    gray = img.convert("L")
    gray = ImageOps.autocontrast(gray)
    # binarizacion simple: mejora el OCR en documentos escaneados con ruido/sombras
    threshold = 180
    return gray.point(lambda p: 255 if p > threshold else 0)


def extract_page_text(page: "fitz.Page", lang: str) -> str:
    text = page.get_text().strip()
    if len(text) >= MIN_CHARS_PER_PAGE:
        return text

    # Pagina sin texto extraible (o casi vacia): se asume escaneada -> OCR
    pix = page.get_pixmap(matrix=fitz.Matrix(OCR_ZOOM, OCR_ZOOM))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img = preprocess_for_ocr(img)
    config = "--oem 3 --psm 1"
    if LOCAL_TESSDATA_DIR.is_dir():
        tessdata_path = str(LOCAL_TESSDATA_DIR.resolve()).replace("\\", "/")
        config += f' --tessdata-dir {tessdata_path}'
    return pytesseract.image_to_string(img, lang=lang, config=config).strip()


def convert_pdf(pdf_path: Path, lang: str) -> str:
    pages_text = []
    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            text = extract_page_text(page, lang)
            pages_text.append(f"--- Pagina {page_number} ---\n{text}")
    return "\n\n".join(pages_text)


def resolve_output_path(pdf_path: Path, output_dir: Path) -> Path:
    return output_dir / (pdf_path.stem + ".txt")


def find_pdfs(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.glob("*.pdf"))
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Convierte PDFs a TXT (incluye OCR para PDFs escaneados).")
    parser.add_argument("input", nargs="?", default=None, help="Archivo PDF o carpeta de entrada (default: ./input)")
    parser.add_argument("-o", "--output", default=None, help="Archivo .txt de salida (solo si input es un archivo) o carpeta de salida")
    parser.add_argument("-l", "--lang", default="spa+eng", help="Idioma(s) para OCR, formato Tesseract (default: spa+eng)")
    parser.add_argument("--tesseract-cmd", default=None, help="Ruta al ejecutable de tesseract si no esta en el PATH")
    args = parser.parse_args()

    tesseract_cmd = args.tesseract_cmd or DEFAULT_TESSERACT_CMD
    if Path(tesseract_cmd).exists():
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    input_target = Path(args.input) if args.input else DEFAULT_INPUT_DIR

    if not input_target.exists():
        print(f"Error: no existe '{input_target}'.", file=sys.stderr)
        return 1

    pdf_files = find_pdfs(input_target)
    if not pdf_files:
        print(f"No se encontraron archivos PDF en '{input_target}'.", file=sys.stderr)
        return 1

    if input_target.is_file() and args.output:
        output_dir = None
        single_output = Path(args.output)
    else:
        output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        single_output = None

    for pdf_path in pdf_files:
        out_path = single_output if single_output else resolve_output_path(pdf_path, output_dir)
        print(f"Procesando: {pdf_path} -> {out_path}")
        try:
            text = convert_pdf(pdf_path, args.lang)
        except Exception as exc:
            print(f"  Error al procesar '{pdf_path}': {exc}", file=sys.stderr)
            continue
        out_path.write_text(text, encoding="utf-8")

    print("Listo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
