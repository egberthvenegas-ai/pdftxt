# PDFTXT

Convierte archivos PDF (con texto seleccionable o escaneados) a archivos `.txt`.

- Si la pagina tiene texto extraible, lo extrae directamente (rapido y exacto).
- Si la pagina no tiene texto (PDF escaneado/imagen), aplica OCR con Tesseract,
  con preprocesamiento de imagen (escala de grises, autocontraste, binarizacion)
  para maximizar la precision. Ningun OCR es 100% exacto; la calidad final depende
  de la resolucion y nitidez del escaneo original.

## Requisitos

1. Python 3.10+
2. Tesseract OCR instalado en el sistema (el binario, no solo la libreria de Python):
   - Windows: `winget install --id UB-Mannheim.TesseractOCR` o descarga el instalador desde
     https://github.com/UB-Mannheim/tesseract/wiki
   - Por defecto el script busca el ejecutable en `C:\Program Files\Tesseract-OCR\tesseract.exe`.
     Si esta en otra ruta, usa `--tesseract-cmd "C:\ruta\a\tesseract.exe"`.
3. Dependencias de Python y paquetes de idioma para OCR (se descargan a una carpeta local
   `tessdata/`, sin necesitar permisos de administrador sobre la instalacion de Tesseract):
   ```
   pip install -r requirements.txt
   python setup_tessdata.py
   ```

## Uso

```
python pdf2txt.py                      # procesa todo ./input -> ./output
python pdf2txt.py archivo.pdf          # procesa un solo archivo -> ./output/archivo.txt
python pdf2txt.py carpeta/             # procesa todos los PDF de esa carpeta
python pdf2txt.py archivo.pdf -o salida.txt
python pdf2txt.py -l eng               # fuerza idioma de OCR (default: spa+eng)
python pdf2txt.py --tesseract-cmd "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Crea la carpeta `input/` y coloca ahi tus PDFs si quieres usar el modo por defecto;
los `.txt` resultantes apareceran en `output/`.
